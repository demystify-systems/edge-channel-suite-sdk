"""
Structured Logging for SaaStify Edge SDK

Provides JSON-formatted logging with context for observability in production.
"""

import logging
import json
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

# Context variables for request tracing
job_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('job_context', default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add job context if available
        ctx = job_context.get()
        if ctx:
            log_data["context"] = ctx

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields from extra
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    structured: bool = True,
    service_name: str = "saastify-edge-sdk"
) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Use JSON structured logging
        service_name: Service name for logging context
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set service context
    set_job_context({"service": service_name})


def set_job_context(**kwargs: Any) -> None:
    """
    Set job context for logging.
    
    Args:
        **kwargs: Context key-value pairs (job_id, tenant_id, etc.)
    """
    current = job_context.get() or {}
    current.update(kwargs)
    job_context.set(current)


def clear_job_context() -> None:
    """Clear job context."""
    job_context.set(None)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter with extra context."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with extra fields."""
        extra = kwargs.get('extra', {})
        if 'extra_fields' not in extra:
            extra['extra_fields'] = {}
        
        # Add job context
        ctx = job_context.get()
        if ctx:
            extra['extra_fields'].update(ctx)
        
        kwargs['extra'] = extra
        return msg, kwargs


def get_context_logger(name: str, **context: Any) -> LoggerAdapter:
    """
    Get logger with permanent context.
    
    Args:
        name: Logger name
        **context: Context to add to all log messages
        
    Returns:
        LoggerAdapter with context
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, {'extra_fields': context})


# Example usage and testing
if __name__ == "__main__":
    # Test structured logging
    print("Testing structured logging...")
    setup_logging(level="INFO", structured=True)
    
    logger = get_logger(__name__)
    
    # Set job context
    set_job_context(
        job_id="test-job-123",
        tenant_id="tenant-001",
        pipeline="import"
    )
    
    logger.info("Starting job processing")
    logger.warning("High memory usage detected", extra={
        'extra_fields': {'memory_mb': 1024}
    })
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Job processing failed", exc_info=True)
    
    logger.info("Job completed successfully")
    
    clear_job_context()
    logger.info("Context cleared")
