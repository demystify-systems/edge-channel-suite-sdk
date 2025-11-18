"""
JSON file parser
"""

import json
from typing import AsyncIterator, Dict, Any, Optional
from .base import BaseParser
from ..types import FileConfig


class JSONParser(BaseParser):
    """Parser for JSON files"""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is JSON"""
        return file_path.lower().endswith('.json')
    
    async def parse(self, file_path: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Parse JSON file and yield rows.
        
        Expects JSON to be either:
        - An array of objects: [{...}, {...}, ...]
        - An object with an array property
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # If data is a list, iterate through it
        if isinstance(data, list):
            for row_num, item in enumerate(data, start=1):
                if isinstance(item, dict):
                    yield {
                        "file_row_number": row_num,
                        "data": item,
                        "raw_input_snapshot": item.copy()
                    }
        
        # If data is a dict, try to find the array
        elif isinstance(data, dict):
            # Look for common array keys
            for key in ['data', 'items', 'rows', 'records', 'products']:
                if key in data and isinstance(data[key], list):
                    for row_num, item in enumerate(data[key], start=1):
                        if isinstance(item, dict):
                            yield {
                                "file_row_number": row_num,
                                "data": item,
                                "raw_input_snapshot": item.copy()
                            }
                    return
            
            # If no array found, treat the whole object as a single row
            yield {
                "file_row_number": 1,
                "data": data,
                "raw_input_snapshot": data.copy()
            }
