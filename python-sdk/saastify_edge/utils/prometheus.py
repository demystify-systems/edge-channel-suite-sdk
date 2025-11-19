"""
Prometheus Metrics Export

Provides Prometheus-compatible metrics export for observability.
"""

from typing import Dict, Any, Optional
from .metrics import MetricsCollector, JobMetrics


class PrometheusExporter:
    """Export metrics in Prometheus format."""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize Prometheus exporter.
        
        Args:
            metrics_collector: Optional metrics collector instance
        """
        from .metrics import get_metrics
        self.metrics = metrics_collector or get_metrics()
    
    def export(self) -> str:
        """
        Export all metrics in Prometheus text format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        # Export counters
        for key, value in self.metrics.counters.items():
            metric_name, tags = self._parse_key(key)
            prom_name = self._sanitize_metric_name(metric_name)
            tag_str = self._format_tags(tags)
            lines.append(f"{prom_name}_total{{{tag_str}}} {value}")
        
        # Export gauges
        for key, value in self.metrics.gauges.items():
            metric_name, tags = self._parse_key(key)
            prom_name = self._sanitize_metric_name(metric_name)
            tag_str = self._format_tags(tags)
            lines.append(f"{prom_name}{{{tag_str}}} {value}")
        
        # Export timers (as histograms/summaries)
        for key, durations in self.metrics.timers.items():
            if not durations:
                continue
            
            metric_name, tags = self._parse_key(key)
            prom_name = self._sanitize_metric_name(metric_name)
            tag_str = self._format_tags(tags)
            
            # Export as summary with count, sum, min, max
            count = len(durations)
            total = sum(durations)
            min_val = min(durations)
            max_val = max(durations)
            avg_val = total / count if count > 0 else 0
            
            lines.append(f"{prom_name}_count{{{tag_str}}} {count}")
            lines.append(f"{prom_name}_sum{{{tag_str}}} {total}")
            lines.append(f"{prom_name}_min{{{tag_str}}} {min_val}")
            lines.append(f"{prom_name}_max{{{tag_str}}} {max_val}")
            lines.append(f"{prom_name}_avg{{{tag_str}}} {avg_val}")
        
        return "\n".join(lines) + "\n"
    
    def export_job_metrics(self, job_metrics: JobMetrics) -> str:
        """
        Export job-specific metrics in Prometheus format.
        
        Args:
            job_metrics: JobMetrics instance
            
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        tags = f'job_id="{job_metrics.job_id}",job_type="{job_metrics.job_type}"'
        
        # Export counters
        for name, value in job_metrics.metrics.get("counters", {}).items():
            prom_name = self._sanitize_metric_name(f"job_{name}")
            lines.append(f"{prom_name}{{{tags}}} {value}")
        
        # Export stage durations
        for stage_name, stage_data in job_metrics.metrics.get("stages", {}).items():
            if "duration_seconds" in stage_data:
                prom_name = self._sanitize_metric_name(f"job_stage_duration_seconds")
                stage_tags = f'{tags},stage="{stage_name}"'
                lines.append(f"{prom_name}{{{stage_tags}}} {stage_data['duration_seconds']}")
        
        # Export total duration
        if "total_duration_seconds" in job_metrics.metrics:
            prom_name = self._sanitize_metric_name("job_total_duration_seconds")
            lines.append(f"{prom_name}{{{tags}}} {job_metrics.metrics['total_duration_seconds']}")
        
        # Export error count
        if "error_count" in job_metrics.metrics:
            prom_name = self._sanitize_metric_name("job_errors_total")
            lines.append(f"{prom_name}{{{tags}}} {job_metrics.metrics['error_count']}")
        
        return "\n".join(lines) + "\n"
    
    def _parse_key(self, key: str) -> tuple:
        """Parse metric key into name and tags."""
        if "[" in key and key.endswith("]"):
            name, tag_str = key.rsplit("[", 1)
            tag_str = tag_str.rstrip("]")
            tags = {}
            for pair in tag_str.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    tags[k.strip()] = v.strip()
            return name, tags
        return key, {}
    
    def _format_tags(self, tags: Dict[str, str]) -> str:
        """Format tags as Prometheus label string."""
        if not tags:
            return ""
        return ",".join(f'{k}="{v}"' for k, v in sorted(tags.items()))
    
    def _sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric name for Prometheus."""
        # Replace invalid characters with underscores
        import re
        name = re.sub(r'[^a-zA-Z0-9_:]', '_', name)
        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = f"metric_{name}"
        return name


def export_prometheus_metrics(metrics_collector: Optional[MetricsCollector] = None) -> str:
    """
    Convenience function to export metrics in Prometheus format.
    
    Args:
        metrics_collector: Optional metrics collector instance
    
    Returns:
        Prometheus-formatted metrics string
    """
    exporter = PrometheusExporter(metrics_collector)
    return exporter.export()


def create_prometheus_endpoint_handler():
    """
    Create a simple HTTP endpoint handler for Prometheus scraping.
    
    Returns:
        Handler function for HTTP server
    """
    def handler(request):
        """Handle Prometheus metrics request."""
        from http.server import BaseHTTPRequestHandler
        exporter = PrometheusExporter()
        metrics_text = exporter.export()
        
        # If this is being used with a real HTTP server, return response
        # For now, just return the metrics text
        return metrics_text
    
    return handler


# Example usage
if __name__ == "__main__":
    from .metrics import increment, set_gauge, timer
    
    # Generate some test metrics
    increment("requests_total", tags={"endpoint": "/import"})
    increment("requests_total", tags={"endpoint": "/export"})
    set_gauge("queue_size", 150)
    
    with timer("operation_duration", tags={"operation": "transform"}):
        import time
        time.sleep(0.1)
    
    # Export to Prometheus format
    exporter = PrometheusExporter()
    print("Prometheus Metrics:")
    print(exporter.export())

