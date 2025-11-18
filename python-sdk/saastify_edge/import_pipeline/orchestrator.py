"""
Import Pipeline Orchestrator - End-to-end import workflow.

Stages:
1. IMPORT_FILE_FETCH - Download file from source
2. IMPORT_FILE_PARSE - Parse file format
3. IMPORT_TEMPLATE_MAP - Map columns to template fields
4. IMPORT_TRANSFORM - Apply transformations
5. IMPORT_VALIDATE - Validate data
6. IMPORT_WRITE_CACHE - Write to completeness cache
7. IMPORT_DB_WRITE - Upsert to product tables
8. IMPORT_COMPLETE - Finalize job
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid

from ..core.loaders import FileLoaderFactory
from ..core.parsers import ParserFactory
from ..transformations.engine import apply_transformations
from ..validation.engine import validate_field, validate_row
from ..db.completeness_cache import CompletenessWriter
from ..db.job_manager import JobStatusUpdater
from .template_mapper import TemplateMapper
from .batch_processor import BatchProcessor, BatchConfig

logger = logging.getLogger(__name__)


class ImportPipelineConfig:
    """Configuration for import pipeline."""

    def __init__(
        self,
        file_source: str,
        template_id: str,
        saas_edge_id: str,
        job_name: Optional[str] = None,
        batch_size: int = 500,
        max_workers: int = 4,
        file_loader_config: Optional[Dict[str, Any]] = None,
        db_client: Optional[Any] = None,
    ):
        self.file_source = file_source
        self.template_id = template_id
        self.saas_edge_id = saas_edge_id
        self.job_name = job_name or f"Import-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.file_loader_config = file_loader_config or {}
        self.db_client = db_client


class ImportPipeline:
    """Orchestrates end-to-end import workflow."""

    def __init__(self, config: ImportPipelineConfig):
        """
        Initialize import pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.template_mapper = TemplateMapper(db_client=config.db_client)
        self.batch_processor = BatchProcessor(
            BatchConfig(
                batch_size=config.batch_size,
                max_workers=config.max_workers,
            )
        )
        self.job_manager = JobStatusUpdater(db_client=config.db_client)
        self.completeness_writer = CompletenessWriter(db_client=config.db_client)
        
        self.job_id: Optional[str] = None
        self.template = None
        self.local_file_path: Optional[str] = None

    async def run(self) -> Dict[str, Any]:
        """
        Execute full import pipeline.
        
        Returns:
            Job results with metrics
        """
        try:
            # Create job record
            self.job_id = str(uuid.uuid4())
            await self.job_manager.create_job(
                job_id=self.job_id,
                job_name=self.config.job_name,
                job_type="IMPORT",
                saas_edge_id=self.config.saas_edge_id,
                request_args={
                    "file_source": self.config.file_source,
                    "template_id": self.config.template_id,
                },
            )
            logger.info(f"Started import job {self.job_id}")

            # Stage 1: Fetch file
            await self._fetch_file()

            # Stage 2: Parse file and load template
            await self._parse_file_setup()

            # Stage 3-6: Process data (transform, validate, cache)
            results = await self._process_data()

            # Stage 7: DB write (mock for now)
            await self._write_to_database(results)

            # Stage 8: Complete job
            await self.job_manager.complete_job(
                job_id=self.job_id,
                job_response={
                    "total_rows": results["total_processed"],
                    "valid_rows": results["total_processed"] - results["total_errors"],
                    "error_rows": results["total_errors"],
                },
            )

            logger.info(f"Import job {self.job_id} completed successfully")
            return results

        except Exception as e:
            logger.error(f"Import job {self.job_id} failed: {e}")
            if self.job_id:
                await self.job_manager.fail_job(
                    job_id=self.job_id,
                    error_message=str(e),
                )
            raise

    async def _fetch_file(self) -> None:
        """Stage 1: Fetch file from source."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="IMPORT_FILE_FETCH",
        )

        logger.info(f"Fetching file from {self.config.file_source}")
        start_time = datetime.now()

        self.local_file_path = await FileLoaderFactory.load_file(
            source=self.config.file_source,
            config=self.config.file_loader_config,
        )

        await self.job_manager.complete_step(
            job_id=self.job_id,
            step_name="file_fetch",
            metrics={
                "file_path": self.local_file_path,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            },
        )

    async def _parse_file_setup(self) -> None:
        """Stage 2: Setup parser and load template."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="IMPORT_FILE_PARSE",
        )

        # Load template
        logger.info(f"Loading template {self.config.template_id}")
        self.template = await self.template_mapper.load_template(
            template_id=self.config.template_id,
            saas_edge_id=self.config.saas_edge_id,
        )

        await self.job_manager.update_status(
            job_id=self.job_id,
            status="IMPORT_TEMPLATE_MAP",
        )

    async def _process_data(self) -> Dict[str, Any]:
        """Stage 3-6: Transform, validate, and cache data."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="IMPORT_TRANSFORM",
        )

        # Create parser
        parser = ParserFactory.create_parser(
            file_path=self.local_file_path,
        )

        # Parse file as async stream
        data_stream = parser.parse_async()

        # Process batches
        results = await self.batch_processor.process_stream(
            data_stream=data_stream,
            processor_func=self._process_batch,
            on_batch_complete=self._on_batch_complete,
        )

        return results

    async def _process_batch(self, batch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single batch of rows.
        
        Args:
            batch_data: List of raw rows from file
            
        Returns:
            Result with success/error counts
        """
        success_count = 0
        error_count = 0
        errors = []

        completeness_records = []

        for row_idx, raw_row in enumerate(batch_data):
            try:
                # Map columns to fields
                mapped_data = self.template_mapper.map_row_to_fields(
                    raw_row=raw_row,
                    template=self.template,
                )

                # Transform fields
                transformed_data = {}
                for field_name, raw_value in mapped_data.items():
                    transformations = self.template_mapper.get_transformation_pipeline(
                        template=self.template,
                        field_name=field_name,
                    )
                    
                    # Convert transformation steps to rule strings
                    if transformations:
                        rule_parts = []
                        for trans in transformations:
                            if trans.args:
                                # Format with args: "operation|arg1|arg2"
                                args_str = "|".join(str(v) for v in trans.args.values())
                                rule_parts.append(f"{trans.operation}|{args_str}")
                            else:
                                rule_parts.append(trans.operation)
                        rule_string = " + ".join(rule_parts)
                        transformed_value = apply_transformations(raw_value, rule_string)
                    else:
                        transformed_value = raw_value
                    
                    transformed_data[field_name] = transformed_value

                # Validate fields
                validation_errors = {}
                for field_name, value in transformed_data.items():
                    validation_rules = self.template_mapper.get_validation_rules(
                        template=self.template,
                        field_name=field_name,
                    )
                    
                    for rule in validation_rules:
                        error = validate_field(
                            value=value,
                            rule_name=rule.rule,
                            **rule.args,
                        )
                        if error:
                            if field_name not in validation_errors:
                                validation_errors[field_name] = []
                            validation_errors[field_name].append(error)

                # Validate row-level
                row_errors = validate_row(transformed_data, self.template)
                if row_errors:
                    validation_errors["_row"] = row_errors

                is_valid = len(validation_errors) == 0

                # Create completeness cache record
                completeness_records.append({
                    "job_id": self.job_id,
                    "run_type": "IMPORT",
                    "saas_edge_id": self.config.saas_edge_id,
                    "template_id": self.config.template_id,
                    "transformed_response": transformed_data,
                    "validation_errors": validation_errors,
                    "is_valid": is_valid,
                    "error_count": len(validation_errors),
                    "file_row_number": row_idx + 1,
                    "raw_input_snapshot": raw_row,
                })

                if is_valid:
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Row {row_idx} processing failed: {e}")
                error_count += 1
                errors.append({"row": row_idx, "error": str(e)})

        # Write to completeness cache
        if completeness_records:
            await self.completeness_writer.write_batch(completeness_records)

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }

    async def _on_batch_complete(self, result) -> None:
        """Callback when a batch completes."""
        logger.debug(
            f"Batch {result.batch_id} complete: "
            f"{result.success_count} success, {result.error_count} errors"
        )

    async def _write_to_database(self, results: Dict[str, Any]) -> None:
        """Stage 7: Write valid records to product database."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="IMPORT_DB_WRITE",
        )

        # In production, this would:
        # 1. Fetch valid records from completeness cache
        # 2. Upsert to product tables via GraphQL/SQL
        # For now, just log
        logger.info(
            f"Would write {results['total_processed'] - results['total_errors']} "
            f"valid rows to database"
        )

        await self.job_manager.complete_step(
            job_id=self.job_id,
            step_name="db_write",
            metrics={
                "rows_written": results["total_processed"] - results["total_errors"],
            },
        )


async def run_product_import(config: ImportPipelineConfig) -> Dict[str, Any]:
    """
    Convenience function to run import pipeline.
    
    Args:
        config: Import configuration
        
    Returns:
        Job results
    """
    pipeline = ImportPipeline(config)
    return await pipeline.run()
