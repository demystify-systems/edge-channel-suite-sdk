"""
Type definitions for the SaaStify Edge SDK
"""

from typing import Any, Dict, List, Optional, Union, TypedDict
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    """Job type enumeration"""
    PRODUCT_IMPORT = "PRODUCT_IMPORT"
    VARIANT_IMPORT = "VARIANT_IMPORT"
    PRODUCT_EXPORT = "PRODUCT_EXPORT"
    CATEGORY_EXPORT = "CATEGORY_EXPORT"


class RunType(str, Enum):
    """Run type for completeness cache"""
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"


class JobStatus(str, Enum):
    """Job status enumeration"""
    # Import stages
    IMPORT_INIT = "IMPORT_INIT"
    IMPORT_FILE_FETCH = "IMPORT_FILE_FETCH"
    IMPORT_FILE_PARSE = "IMPORT_FILE_PARSE"
    IMPORT_TEMPLATE_MAP = "IMPORT_TEMPLATE_MAP"
    IMPORT_TRANSFORM = "IMPORT_TRANSFORM"
    IMPORT_VALIDATE = "IMPORT_VALIDATE"
    IMPORT_WRITE_CACHE = "IMPORT_WRITE_CACHE"
    IMPORT_WRITE_DB = "IMPORT_WRITE_DB"
    IMPORT_POSTPROCESS = "IMPORT_POSTPROCESS"
    
    # Export stages
    EXPORT_INIT = "EXPORT_INIT"
    EXPORT_LOAD_TEMPLATE = "EXPORT_LOAD_TEMPLATE"
    EXPORT_FETCH_PRODUCTS = "EXPORT_FETCH_PRODUCTS"
    EXPORT_TRANSFORM = "EXPORT_TRANSFORM"
    EXPORT_VALIDATE = "EXPORT_VALIDATE"
    EXPORT_WRITE_CACHE = "EXPORT_WRITE_CACHE"
    EXPORT_BUILD_FILE = "EXPORT_BUILD_FILE"
    EXPORT_UPLOAD_FILE = "EXPORT_UPLOAD_FILE"
    EXPORT_NOTIFY = "EXPORT_NOTIFY"
    
    # Terminal states
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FileFormat(str, Enum):
    """Supported file formats"""
    CSV = "CSV"
    TSV = "TSV"
    XLSX = "XLSX"
    XLSM = "XLSM"
    JSON = "JSON"
    XML = "XML"


class TransformationStep(TypedDict, total=False):
    """A single transformation step"""
    operation: str
    args: Dict[str, Any]


class ValidationRule(TypedDict, total=False):
    """A single validation rule"""
    rule: str
    args: Dict[str, Any]
    error_message: Optional[str]


class AttributeDefinition(TypedDict):
    """Attribute definition in a template"""
    name: str
    column_name: str
    data_type: str
    is_required: bool
    transformations: List[TransformationStep]
    validations: List[ValidationRule]


class ChannelTemplate(TypedDict):
    """Channel template structure"""
    id: str
    channel_name: str
    template_name: str
    attributes: List[AttributeDefinition]


class ValidationError(TypedDict):
    """Validation error structure"""
    field: str
    rule: str
    message: str
    value: Optional[Any]


class FileConfig(TypedDict, total=False):
    """File configuration for parsing"""
    delimiter: str
    header_row: int
    fixed_rows: int
    sheet_name: Optional[str]


class FeedSettings(TypedDict, total=False):
    """Feed settings for import"""
    create_new_product: bool
    skip_errors: bool
    batch_size: int
    concurrency: int


class ExportFormats(TypedDict, total=False):
    """Export format configuration"""
    formats: List[FileFormat]
    split_size: Optional[int]


class CompletenessRecord(TypedDict):
    """Product template completeness cache record"""
    internal_id: str
    job_id: str
    run_type: RunType
    saas_edge_id: str
    product_id: Optional[str]
    template_id: str
    transformed_response: Dict[str, Any]
    validation_errors: Dict[str, List[ValidationError]]
    is_valid: bool
    error_count: int
    cache_freshness: bool
    processing_status: str
    file_row_number: Optional[int]
    raw_input_snapshot: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ImportContext(TypedDict):
    """Import pipeline context"""
    job_id: str
    saas_edge_id: str
    template_id: str
    file_url: str
    feed_settings: FeedSettings


class ExportContext(TypedDict):
    """Export pipeline context"""
    job_id: str
    saas_edge_id: str
    template_id: str
    entity_type: str
    filter_params: Dict[str, Any]
    formats: ExportFormats


class ImportResult(TypedDict):
    """Import operation result"""
    job_id: str
    total_rows: int
    success_count: int
    failed_count: int
    error_details: Optional[List[Dict[str, Any]]]


class ExportResult(TypedDict):
    """Export operation result"""
    job_id: str
    total_rows: int
    success_count: int
    failed_count: int
    file_urls: List[str]


class RejectRow(Exception):
    """Exception to mark row for rejection during transformation"""
    pass
