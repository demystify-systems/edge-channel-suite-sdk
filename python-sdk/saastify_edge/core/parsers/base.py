"""
Base parser class for file parsing
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
from ..types import FileConfig


class BaseParser(ABC):
    """Abstract base class for file parsers"""
    
    def __init__(self, file_config: Optional[FileConfig] = None):
        """
        Initialize parser with configuration.
        
        Args:
            file_config: File parsing configuration (delimiter, header row, etc.)
        """
        self.file_config = file_config or {}
        self.header_row = self.file_config.get("header_row", 1)
        self.fixed_rows = self.file_config.get("fixed_rows", 0)
        self.delimiter = self.file_config.get("delimiter", ",")
        self.sheet_name = self.file_config.get("sheet_name")
    
    @abstractmethod
    async def parse(self, file_path: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Parse file and yield rows as dictionaries.
        
        Args:
            file_path: Path to the file to parse
        
        Yields:
            Dictionary representing each row with file_row_number and data
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if this parser can handle the file
        """
        pass
