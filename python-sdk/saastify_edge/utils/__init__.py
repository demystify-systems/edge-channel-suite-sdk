"""Utilities for logging and metrics collection."""

from .logging import (
    setup_logging,
    get_logger,
    get_context_logger,
    set_job_context,
    clear_job_context,
)

from .metrics import (
    MetricsCollector,
    JobMetrics,
    get_metrics,
    increment,
    set_gauge,
    record_time,
    timer,
    get_summary,
    reset_metrics,
)

from .prometheus import (
    PrometheusExporter,
    export_prometheus_metrics,
    create_prometheus_endpoint_handler,
)

from .sanitization import (
    sanitize_html,
    sanitize_scripts,
    sanitize_sql_injection,
    sanitize_filename,
    sanitize_text,
    sanitize_url,
    sanitize_row,
    sanitize_input,
)

from .template_schema import (
    generate_json_schema,
    get_or_generate_template_schema,
)

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "get_context_logger",
    "set_job_context",
    "clear_job_context",
    # Metrics
    "MetricsCollector",
    "JobMetrics",
    "get_metrics",
    "increment",
    "set_gauge",
    "record_time",
    "timer",
    "get_summary",
    "reset_metrics",
    # Prometheus
    "PrometheusExporter",
    "export_prometheus_metrics",
    "create_prometheus_endpoint_handler",
    # Sanitization
    "sanitize_html",
    "sanitize_scripts",
    "sanitize_sql_injection",
    "sanitize_filename",
    "sanitize_text",
    "sanitize_url",
    "sanitize_row",
    "sanitize_input",
    # Template Schema
    "generate_json_schema",
    "get_or_generate_template_schema",
]