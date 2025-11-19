"""
Input Sanitization Utilities

Provides utilities for sanitizing input data to prevent injection attacks
and ensure data safety.
"""

import re
import html
from typing import Any, Optional, Dict


def sanitize_html(value: Any, remove_tags: bool = True, allowed_tags: Optional[list] = None) -> Any:
    """
    Sanitize HTML content by removing or escaping potentially dangerous elements.
    
    Args:
        value: Input value (string or other)
        remove_tags: If True, remove all HTML tags. If False, escape them.
        allowed_tags: Optional list of allowed HTML tags (if remove_tags=False)
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    if remove_tags:
        # Remove all HTML tags
        value = re.sub(r'<[^>]+>', '', value)
    elif allowed_tags:
        # Remove all tags except allowed ones
        allowed_pattern = '|'.join(re.escape(tag) for tag in allowed_tags)
        # Remove all tags not in allowed list
        value = re.sub(rf'<(?!\/?(?:{allowed_pattern})\b)[^>]+>', '', value, flags=re.IGNORECASE)
    else:
        # Escape HTML entities
        value = html.escape(value)
    
    return value


def sanitize_scripts(value: Any) -> Any:
    """
    Remove script tags and JavaScript event handlers.
    
    Args:
        value: Input value
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    # Remove script tags
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove JavaScript event handlers (onclick, onerror, etc.)
    value = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    
    return value


def sanitize_sql_injection(value: Any) -> Any:
    """
    Basic SQL injection prevention by escaping quotes.
    
    Note: This is a basic sanitization. For production, use parameterized queries.
    
    Args:
        value: Input value
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    # Escape single quotes
    value = value.replace("'", "''")
    
    # Remove SQL comment markers
    value = value.replace("--", "")
    value = value.replace("/*", "")
    value = value.replace("*/", "")
    
    return value


def sanitize_filename(value: Any) -> Any:
    """
    Sanitize filename to remove dangerous characters.
    
    Args:
        value: Input filename
    
    Returns:
        Sanitized filename
    """
    if not isinstance(value, str):
        return value
    
    # Remove path separators
    value = value.replace("/", "_").replace("\\", "_")
    
    # Remove dangerous characters
    value = re.sub(r'[<>:"|?*]', '', value)
    
    # Remove control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Limit length
    if len(value) > 255:
        value = value[:255]
    
    return value


def sanitize_text(value: Any, max_length: Optional[int] = None, 
                  remove_emojis: bool = False, remove_control_chars: bool = True) -> Any:
    """
    General text sanitization.
    
    Args:
        value: Input value
        max_length: Optional maximum length
        remove_emojis: Remove emoji characters
        remove_control_chars: Remove control characters
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    # Remove control characters
    if remove_control_chars:
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Remove emojis
    if remove_emojis:
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"   # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+", flags=re.UNICODE
        )
        value = emoji_pattern.sub('', value)
    
    # Limit length
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def sanitize_url(value: Any, allowed_schemes: Optional[list] = None) -> Any:
    """
    Sanitize URL to prevent XSS and protocol injection.
    
    Args:
        value: Input URL
        allowed_schemes: Optional list of allowed URL schemes (default: http, https)
    
    Returns:
        Sanitized URL or None if invalid
    """
    if not isinstance(value, str):
        return value
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    # Check if URL has allowed scheme
    for scheme in allowed_schemes:
        if value.lower().startswith(f"{scheme}://"):
            # Basic validation - remove javascript: and data: protocols
            if 'javascript:' in value.lower() or value.lower().startswith('data:'):
                return None
            return value
    
    # If no scheme, assume http
    if not value.startswith(('http://', 'https://')):
        return f"http://{value}"
    
    return None


def sanitize_row(row: Dict[str, Any], sanitization_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Sanitize an entire row of data based on configuration.
    
    Args:
        row: Dictionary of field values
        sanitization_config: Optional configuration dict mapping field names to sanitization functions
    
    Returns:
        Sanitized row
    """
    sanitized_row = {}
    config = sanitization_config or {}
    
    for field_name, value in row.items():
        # Get sanitization function for this field
        sanitize_func = config.get(field_name)
        
        if sanitize_func:
            if callable(sanitize_func):
                sanitized_row[field_name] = sanitize_func(value)
            elif isinstance(sanitize_func, dict):
                # Config dict with options
                func_name = sanitize_func.get('function', 'sanitize_text')
                func_kwargs = sanitize_func.get('kwargs', {})
                
                if func_name == 'sanitize_html':
                    sanitized_row[field_name] = sanitize_html(value, **func_kwargs)
                elif func_name == 'sanitize_scripts':
                    sanitized_row[field_name] = sanitize_scripts(value)
                elif func_name == 'sanitize_text':
                    sanitized_row[field_name] = sanitize_text(value, **func_kwargs)
                elif func_name == 'sanitize_filename':
                    sanitized_row[field_name] = sanitize_filename(value)
                elif func_name == 'sanitize_url':
                    sanitized_row[field_name] = sanitize_url(value, **func_kwargs)
                else:
                    sanitized_row[field_name] = value
            else:
                sanitized_row[field_name] = value
        else:
            # Default: basic text sanitization
            sanitized_row[field_name] = sanitize_text(value)
    
    return sanitized_row


# Convenience function for common sanitization
def sanitize_input(value: Any, input_type: str = 'text') -> Any:
    """
    Convenience function for common sanitization tasks.
    
    Args:
        value: Input value
        input_type: Type of input ('text', 'html', 'url', 'filename', 'sql')
    
    Returns:
        Sanitized value
    """
    if input_type == 'html':
        return sanitize_html(value, remove_tags=True)
    elif input_type == 'url':
        return sanitize_url(value)
    elif input_type == 'filename':
        return sanitize_filename(value)
    elif input_type == 'sql':
        return sanitize_sql_injection(value)
    else:  # 'text' or default
        return sanitize_text(value)


# Example usage
if __name__ == "__main__":
    # Test HTML sanitization
    html_input = '<p>Hello <script>alert("XSS")</script> World</p>'
    print(f"HTML input: {html_input}")
    print(f"Sanitized: {sanitize_html(html_input)}")
    
    # Test script removal
    script_input = '<div onclick="alert(\'XSS\')">Click me</div>'
    print(f"\nScript input: {script_input}")
    print(f"Sanitized: {sanitize_scripts(script_input)}")
    
    # Test filename sanitization
    filename = "../../etc/passwd"
    print(f"\nFilename input: {filename}")
    print(f"Sanitized: {sanitize_filename(filename)}")
    
    # Test URL sanitization
    url = "javascript:alert('XSS')"
    print(f"\nURL input: {url}")
    print(f"Sanitized: {sanitize_url(url)}")

