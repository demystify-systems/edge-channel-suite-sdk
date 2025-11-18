"""
CSV/TSV file parser with streaming support
"""

import csv
from typing import AsyncIterator, Dict, Any, Optional, List
from .base import BaseParser
from ..types import FileConfig


class CSVParser(BaseParser):
    """Parser for CSV and TSV files"""
    
    def __init__(self, file_config: Optional[FileConfig] = None):
        super().__init__(file_config)
        # Auto-detect delimiter if not specified
        if not self.delimiter:
            self.delimiter = ","
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is CSV or TSV"""
        return file_path.lower().endswith(('.csv', '.tsv', '.txt'))
    
    async def parse(self, file_path: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Parse CSV/TSV file and yield rows.
        
        Yields rows as dictionaries with file_row_number and field data.
        """
        # Auto-detect TSV
        if file_path.lower().endswith('.tsv'):
            self.delimiter = '\t'
        
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
            # Skip fixed rows
            for _ in range(self.fixed_rows):
                next(f, None)
            
            # Create CSV reader
            reader = csv.reader(f, delimiter=self.delimiter)
            
            # Read header
            headers: Optional[List[str]] = None
            for row_num, row in enumerate(reader, start=1):
                if row_num == self.header_row:
                    headers = [col.strip() if col else f"Column_{i}" 
                              for i, col in enumerate(row)]
                    continue
                
                # Skip rows before data starts
                if headers is None:
                    continue
                
                # Build row dictionary
                row_data = {}
                for i, value in enumerate(row):
                    col_name = headers[i] if i < len(headers) else f"Column_{i}"
                    row_data[col_name] = value.strip() if value else None
                
                yield {
                    "file_row_number": row_num,
                    "data": row_data,
                    "raw_input_snapshot": row_data.copy()
                }


class TSVParser(CSVParser):
    """Parser specifically for TSV files (inherits from CSVParser)"""
    
    def __init__(self, file_config: Optional[FileConfig] = None):
        super().__init__(file_config)
        self.delimiter = '\t'
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is TSV"""
        return file_path.lower().endswith('.tsv')
