"""
Parser factory for auto-detecting and creating the appropriate parser
"""

from typing import Optional
from .base import BaseParser
from .csv_parser import CSVParser, TSVParser
from .excel_parser import ExcelParser
from .json_parser import JSONParser
from .xml_parser import XMLParser
from ..types import FileConfig


# Registry of all available parsers
PARSER_CLASSES = [
    TSVParser,      # Check TSV before CSV
    CSVParser,
    ExcelParser,
    JSONParser,
    XMLParser,
]


def get_parser(file_path: str, file_config: Optional[FileConfig] = None) -> BaseParser:
    """
    Get the appropriate parser for a file based on its extension.
    
    Args:
        file_path: Path to the file
        file_config: Optional file configuration
    
    Returns:
        Parser instance
    
    Raises:
        ValueError: If no suitable parser is found
    """
    for parser_class in PARSER_CLASSES:
        parser = parser_class(file_config)
        if parser.can_parse(file_path):
            return parser
    
    raise ValueError(f"No parser available for file: {file_path}")


def detect_file_type(file_path: str) -> str:
    """
    Detect the file type based on extension.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File type string (CSV, TSV, XLSX, JSON, XML, UNKNOWN)
    """
    lower_path = file_path.lower()
    
    if lower_path.endswith('.csv'):
        return 'CSV'
    elif lower_path.endswith('.tsv'):
        return 'TSV'
    elif lower_path.endswith(('.xlsx', '.xlsm')):
        return 'XLSX'
    elif lower_path.endswith('.xls'):
        return 'XLS'
    elif lower_path.endswith('.json'):
        return 'JSON'
    elif lower_path.endswith('.xml'):
        return 'XML'
    else:
        return 'UNKNOWN'


class ParserFactory:
    """Factory class for creating parsers."""
    
    @staticmethod
    def create_parser(file_path: str, file_config: Optional[FileConfig] = None) -> BaseParser:
        """Alias for get_parser for consistent naming with other factories."""
        return get_parser(file_path, file_config)
    
    @staticmethod
    def detect_type(file_path: str) -> str:
        """Alias for detect_file_type for consistent naming."""
        return detect_file_type(file_path)
