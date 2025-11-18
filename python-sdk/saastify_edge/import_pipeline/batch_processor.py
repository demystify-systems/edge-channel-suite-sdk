"""
Batch Processor - Concurrent processing with backpressure control.

Handles:
- Batching rows for efficient processing
- Concurrent worker pools
- Backpressure to prevent memory overflow
- Error handling and retry logic
"""

import asyncio
from typing import List, Dict, Any, Callable, Optional, AsyncIterator
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 500  # Rows per batch
    max_workers: int = 4  # Concurrent workers
    max_queue_size: int = 10  # Max batches in queue
    timeout_seconds: float = 300.0  # 5 minutes per batch
    retry_attempts: int = 3  # Retry failed batches
    backpressure_enabled: bool = True


@dataclass
class BatchResult:
    """Result of processing a single batch."""
    batch_id: int
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]
    processing_time: float
    start_time: datetime
    end_time: datetime


class BatchProcessor:
    """Process data in batches with concurrent workers and backpressure."""

    def __init__(self, config: Optional[BatchConfig] = None):
        """
        Initialize batch processor.
        
        Args:
            config: Batch processing configuration
        """
        self.config = config or BatchConfig()
        self._queue: asyncio.Queue = asyncio.Queue(
            maxsize=self.config.max_queue_size if self.config.backpressure_enabled else 0
        )
        self._results: List[BatchResult] = []
        self._total_processed = 0
        self._total_errors = 0
        self._is_running = False

    async def process_stream(
        self,
        data_stream: AsyncIterator[Dict[str, Any]],
        processor_func: Callable[[List[Dict[str, Any]]], Any],
        on_batch_complete: Optional[Callable[[BatchResult], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process streaming data in batches with concurrent workers.
        
        Args:
            data_stream: Async iterator yielding data rows
            processor_func: Function to process each batch (can be sync or async)
            on_batch_complete: Optional callback when batch completes
            
        Returns:
            Summary statistics (total processed, errors, timing)
        """
        start_time = datetime.now()
        self._is_running = True
        self._results.clear()
        self._total_processed = 0
        self._total_errors = 0

        # Start worker pool
        workers = [
            asyncio.create_task(self._worker(i, processor_func, on_batch_complete))
            for i in range(self.config.max_workers)
        ]

        # Producer: batch rows and queue them
        producer_task = asyncio.create_task(
            self._produce_batches(data_stream)
        )

        # Wait for all work to complete
        await producer_task
        await self._queue.join()

        # Stop workers
        self._is_running = False
        for _ in workers:
            await self._queue.put(None)  # Sentinel to stop workers

        await asyncio.gather(*workers, return_exceptions=True)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "total_processed": self._total_processed,
            "total_errors": self._total_errors,
            "total_batches": len(self._results),
            "duration_seconds": duration,
            "throughput_rows_per_second": self._total_processed / duration if duration > 0 else 0,
            "batch_results": self._results,
        }

    async def _produce_batches(self, data_stream: AsyncIterator[Dict[str, Any]]) -> None:
        """
        Read from stream and create batches.
        
        Args:
            data_stream: Async iterator yielding rows
        """
        batch_id = 0
        current_batch: List[Dict[str, Any]] = []

        try:
            async for row in data_stream:
                current_batch.append(row)

                if len(current_batch) >= self.config.batch_size:
                    # Queue is full, backpressure kicks in
                    await self._queue.put((batch_id, current_batch))
                    logger.debug(f"Queued batch {batch_id} with {len(current_batch)} rows")
                    batch_id += 1
                    current_batch = []

            # Queue remaining rows
            if current_batch:
                await self._queue.put((batch_id, current_batch))
                logger.debug(f"Queued final batch {batch_id} with {len(current_batch)} rows")

        except Exception as e:
            logger.error(f"Error producing batches: {e}")
            raise

    async def _worker(
        self,
        worker_id: int,
        processor_func: Callable,
        on_batch_complete: Optional[Callable[[BatchResult], None]],
    ) -> None:
        """
        Worker that processes batches from queue.
        
        Args:
            worker_id: Worker identifier
            processor_func: Function to process batch
            on_batch_complete: Callback on completion
        """
        logger.info(f"Worker {worker_id} started")

        while self._is_running or not self._queue.empty():
            try:
                # Get batch with timeout
                batch_item = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0,
                )

                if batch_item is None:  # Sentinel
                    self._queue.task_done()
                    break

                batch_id, batch_data = batch_item

                # Process with retry logic
                result = await self._process_batch_with_retry(
                    batch_id, batch_data, processor_func
                )

                # Update stats
                self._total_processed += result.success_count
                self._total_errors += result.error_count
                self._results.append(result)

                # Callback
                if on_batch_complete:
                    try:
                        if asyncio.iscoroutinefunction(on_batch_complete):
                            await on_batch_complete(result)
                        else:
                            on_batch_complete(result)
                    except Exception as e:
                        logger.warning(f"Batch complete callback error: {e}")

                self._queue.task_done()
                logger.debug(
                    f"Worker {worker_id} completed batch {batch_id}: "
                    f"{result.success_count} success, {result.error_count} errors"
                )

            except asyncio.TimeoutError:
                continue  # No work available, check again
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                self._queue.task_done()

        logger.info(f"Worker {worker_id} stopped")

    async def _process_batch_with_retry(
        self,
        batch_id: int,
        batch_data: List[Dict[str, Any]],
        processor_func: Callable,
    ) -> BatchResult:
        """
        Process batch with retry logic.
        
        Args:
            batch_id: Batch identifier
            batch_data: List of rows to process
            processor_func: Processing function
            
        Returns:
            BatchResult with success/error counts
        """
        start_time = datetime.now()
        errors = []
        last_exception = None

        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                # Execute processor
                if asyncio.iscoroutinefunction(processor_func):
                    result = await asyncio.wait_for(
                        processor_func(batch_data),
                        timeout=self.config.timeout_seconds,
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(processor_func, batch_data),
                        timeout=self.config.timeout_seconds,
                    )

                end_time = datetime.now()

                # Parse result
                if isinstance(result, dict):
                    success_count = result.get("success_count", len(batch_data))
                    error_count = result.get("error_count", 0)
                    errors = result.get("errors", [])
                else:
                    # Assume success if no dict returned
                    success_count = len(batch_data)
                    error_count = 0
                    errors = []

                return BatchResult(
                    batch_id=batch_id,
                    success_count=success_count,
                    error_count=error_count,
                    errors=errors,
                    processing_time=(end_time - start_time).total_seconds(),
                    start_time=start_time,
                    end_time=end_time,
                )

            except asyncio.TimeoutError:
                last_exception = f"Batch {batch_id} timed out after {self.config.timeout_seconds}s"
                logger.warning(f"{last_exception} (attempt {attempt}/{self.config.retry_attempts})")
            except Exception as e:
                last_exception = str(e)
                logger.warning(
                    f"Batch {batch_id} failed on attempt {attempt}/{self.config.retry_attempts}: {e}"
                )

            # Wait before retry
            if attempt < self.config.retry_attempts:
                await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff

        # All retries failed
        end_time = datetime.now()
        return BatchResult(
            batch_id=batch_id,
            success_count=0,
            error_count=len(batch_data),
            errors=[{"error": f"Batch failed after {self.config.retry_attempts} retries: {last_exception}"}],
            processing_time=(end_time - start_time).total_seconds(),
            start_time=start_time,
            end_time=end_time,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            "total_processed": self._total_processed,
            "total_errors": self._total_errors,
            "batches_completed": len(self._results),
            "is_running": self._is_running,
        }
