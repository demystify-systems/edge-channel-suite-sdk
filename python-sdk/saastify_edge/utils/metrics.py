"""
Metrics Collection for SaaStify Edge SDK

Provides metrics tracking for monitoring and observability.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager


@dataclass
class MetricsCollector:
    """Collects performance and operational metrics."""
    
    counters: Dict[str, int] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)
    timers: Dict[str, list] = field(default_factory=dict)
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter.
        
        Args:
            name: Counter name
            value: Increment value
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge value.
        
        Args:
            name: Gauge name
            value: Gauge value
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        self.gauges[key] = value
    
    def record_time(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a timing metric.
        
        Args:
            name: Timer name
            duration: Duration in seconds
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        if key not in self.timers:
            self.timers[key] = []
        self.timers[key].append(duration)
    
    @contextmanager
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager for timing operations.
        
        Usage:
            with metrics.timer("process_batch"):
                process_data()
        """
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.record_time(name, duration, tags)
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create metric key with tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": {}
        }
        
        # Calculate timer statistics
        for key, durations in self.timers.items():
            if durations:
                summary["timers"][key] = {
                    "count": len(durations),
                    "total": sum(durations),
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                }
        
        return summary
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.timers.clear()


# Global metrics collector
_global_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_metrics


def increment(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
    """Increment a counter (global)."""
    _global_metrics.increment(name, value, tags)


def set_gauge(name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Set a gauge value (global)."""
    _global_metrics.set_gauge(name, value, tags)


def record_time(name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Record a timing metric (global)."""
    _global_metrics.record_time(name, duration, tags)


@contextmanager
def timer(name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager for timing operations (global)."""
    with _global_metrics.timer(name, tags):
        yield


def get_summary() -> Dict[str, Any]:
    """Get summary of all metrics (global)."""
    return _global_metrics.get_summary()


def reset_metrics() -> None:
    """Reset all metrics (global)."""
    _global_metrics.reset()


class JobMetrics:
    """Track metrics for a specific job."""
    
    def __init__(self, job_id: str, job_type: str):
        """
        Initialize job metrics.
        
        Args:
            job_id: Job identifier
            job_type: Job type (IMPORT/EXPORT)
        """
        self.job_id = job_id
        self.job_type = job_type
        self.start_time = time.time()
        self.metrics = {
            "job_id": job_id,
            "job_type": job_type,
            "started_at": datetime.utcnow().isoformat(),
            "stages": {},
            "counters": {},
            "errors": []
        }
        self.current_stage: Optional[str] = None
        self.stage_start: Optional[float] = None
    
    def start_stage(self, stage_name: str) -> None:
        """Start tracking a job stage."""
        if self.current_stage:
            self.end_stage()
        
        self.current_stage = stage_name
        self.stage_start = time.time()
        self.metrics["stages"][stage_name] = {
            "started_at": datetime.utcnow().isoformat(),
            "status": "in_progress"
        }
    
    def end_stage(self, success: bool = True, error: Optional[str] = None) -> None:
        """End current stage tracking."""
        if not self.current_stage or not self.stage_start:
            return
        
        duration = time.time() - self.stage_start
        stage_metrics = self.metrics["stages"][self.current_stage]
        stage_metrics.update({
            "completed_at": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "status": "success" if success else "failed"
        })
        
        if error:
            stage_metrics["error"] = error
            self.metrics["errors"].append({
                "stage": self.current_stage,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.current_stage = None
        self.stage_start = None
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a job-specific counter."""
        self.metrics["counters"][name] = self.metrics["counters"].get(name, 0) + value
    
    def set_metadata(self, **kwargs: Any) -> None:
        """Set metadata for the job."""
        if "metadata" not in self.metrics:
            self.metrics["metadata"] = {}
        self.metrics["metadata"].update(kwargs)
    
    def finalize(self, success: bool = True) -> Dict[str, Any]:
        """Finalize metrics and return summary."""
        if self.current_stage:
            self.end_stage(success=success)
        
        total_duration = time.time() - self.start_time
        self.metrics.update({
            "completed_at": datetime.utcnow().isoformat(),
            "total_duration_seconds": total_duration,
            "final_status": "success" if success else "failed",
            "error_count": len(self.metrics["errors"])
        })
        
        return self.metrics


# Example usage
if __name__ == "__main__":
    print("Testing metrics collection...")
    
    # Test global metrics
    increment("requests_total", tags={"endpoint": "/import"})
    increment("requests_total", tags={"endpoint": "/import"})
    increment("requests_total", tags={"endpoint": "/export"})
    
    set_gauge("queue_size", 150)
    
    with timer("operation_duration", tags={"operation": "transform"}):
        time.sleep(0.1)
    
    with timer("operation_duration", tags={"operation": "validate"}):
        time.sleep(0.05)
    
    print("\nGlobal Metrics Summary:")
    import json
    print(json.dumps(get_summary(), indent=2))
    
    # Test job metrics
    print("\n\nTesting job metrics...")
    job_metrics = JobMetrics("job-123", "IMPORT")
    
    job_metrics.start_stage("FETCH_FILE")
    time.sleep(0.05)
    job_metrics.end_stage(success=True)
    
    job_metrics.start_stage("TRANSFORM")
    job_metrics.increment_counter("rows_processed", 100)
    job_metrics.increment_counter("rows_valid", 95)
    job_metrics.increment_counter("rows_invalid", 5)
    time.sleep(0.1)
    job_metrics.end_stage(success=True)
    
    job_metrics.set_metadata(file_size_mb=5.2, row_count=100)
    
    final_metrics = job_metrics.finalize(success=True)
    print("\nJob Metrics:")
    print(json.dumps(final_metrics, indent=2))
