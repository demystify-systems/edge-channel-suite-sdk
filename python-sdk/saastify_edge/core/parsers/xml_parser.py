"""
XML file parser
"""

import xml.etree.ElementTree as ET
from typing import AsyncIterator, Dict, Any, Optional
from .base import BaseParser
from ..types import FileConfig


class XMLParser(BaseParser):
    """Parser for XML files"""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is XML"""
        return file_path.lower().endswith('.xml')
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            # If element has no children and no attributes, return text directly
            if not list(element) and not element.attrib:
                return element.text.strip()
            result['_text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._element_to_dict(child)
            
            # Handle multiple children with same tag
            if child.tag in result:
                # Convert to list if not already
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result if result else None
    
    async def parse(self, file_path: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Parse XML file and yield rows.
        
        Assumes XML structure with repeating elements representing rows.
        Common patterns:
        - <root><row>...</row><row>...</row></root>
        - <root><items><item>...</item><item>...</item></items></root>
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Try to find repeating elements (items)
        # Common tag names for items
        item_tags = ['row', 'item', 'record', 'product', 'entry', 'data']
        
        items = []
        for tag in item_tags:
            items = root.findall(f".//{tag}")
            if items:
                break
        
        # If no common tags found, use direct children
        if not items:
            items = list(root)
        
        # Yield each item as a row
        for row_num, item in enumerate(items, start=1):
            row_data = self._element_to_dict(item)
            
            if row_data:
                yield {
                    "file_row_number": row_num,
                    "data": row_data if isinstance(row_data, dict) else {"value": row_data},
                    "raw_input_snapshot": row_data if isinstance(row_data, dict) else {"value": row_data}
                }
