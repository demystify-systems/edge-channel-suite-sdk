"""Import pipeline orchestration."""

from .template_mapper import TemplateMapper
from .batch_processor import BatchProcessor, BatchConfig, BatchResult

__all__ = [
    "TemplateMapper",
    "BatchProcessor",
    "BatchConfig",
    "BatchResult",
]

"""
Import pipeline orchestration
"""

from typing import Dict, Any


async def run_product_import(**kwargs) -> Dict[str, Any]:
    """
    Run product import pipeline
    
    TODO: Implement full import pipeline
    """
    raise NotImplementedError("Import pipeline not yet implemented")


__all__ = ["run_product_import"]
