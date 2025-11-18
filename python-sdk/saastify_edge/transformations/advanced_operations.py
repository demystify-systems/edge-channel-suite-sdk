"""
Advanced Transformation Operations

Additional 40+ transformation operations for extended functionality.
"""

import re
import math
from typing import Any, Optional
from datetime import datetime, timedelta


# ============================================================================
# ADVANCED TEXT OPERATIONS
# ============================================================================

def remove_whitespace(v: Any, **kwargs) -> Any:
    """Remove all whitespace from string."""
    if not isinstance(v, str):
        return v
    return re.sub(r'\s+', '', v)


def truncate(v: Any, max_length: int = 100, suffix: str = '...', **kwargs) -> Any:
    """Truncate string to maximum length."""
    if not isinstance(v, str):
        return v
    if len(v) <= max_length:
        return v
    return v[:max_length - len(suffix)] + suffix


def pad_left(v: Any, width: int = 10, fill_char: str = '0', **kwargs) -> Any:
    """Pad string on the left."""
    if v is None:
        return None
    return str(v).rjust(width, fill_char)


def pad_right(v: Any, width: int = 10, fill_char: str = ' ', **kwargs) -> Any:
    """Pad string on the right."""
    if v is None:
        return None
    return str(v).ljust(width, fill_char)


def slugify(v: Any, **kwargs) -> Any:
    """Convert string to URL-friendly slug."""
    if not isinstance(v, str):
        return v
    slug = re.sub(r'[^\w\s-]', '', v.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def extract_numbers(v: Any, **kwargs) -> Any:
    """Extract all numbers from string."""
    if not isinstance(v, str):
        return v
    return ''.join(re.findall(r'\d', v))


def extract_letters(v: Any, **kwargs) -> Any:
    """Extract all letters from string."""
    if not isinstance(v, str):
        return v
    return ''.join(re.findall(r'[a-zA-Z]', v))


def reverse_string(v: Any, **kwargs) -> Any:
    """Reverse a string."""
    if not isinstance(v, str):
        return v
    return v[::-1]


def word_count(v: Any, **kwargs) -> Any:
    """Count words in string."""
    if not isinstance(v, str):
        return 0
    return len(v.split())


def char_count(v: Any, **kwargs) -> Any:
    """Count characters in string."""
    if not isinstance(v, str):
        return 0
    return len(v)


def to_snake_case(v: Any, **kwargs) -> Any:
    """Convert string to snake_case."""
    if not isinstance(v, str):
        return v
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', v)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_camel_case(v: Any, **kwargs) -> Any:
    """Convert string to camelCase."""
    if not isinstance(v, str):
        return v
    components = v.split('_')
    return components[0].lower() + ''.join(x.title() for x in components[1:])


def to_pascal_case(v: Any, **kwargs) -> Any:
    """Convert string to PascalCase."""
    if not isinstance(v, str):
        return v
    return ''.join(x.title() for x in v.split('_'))


def remove_special_chars(v: Any, **kwargs) -> Any:
    """Remove all special characters, keeping only alphanumeric."""
    if not isinstance(v, str):
        return v
    return re.sub(r'[^a-zA-Z0-9\s]', '', v)


def remove_accents(v: Any, **kwargs) -> Any:
    """Remove accents from characters."""
    if not isinstance(v, str):
        return v
    import unicodedata
    return ''.join(
        c for c in unicodedata.normalize('NFD', v)
        if unicodedata.category(c) != 'Mn'
    )


# ============================================================================
# ADVANCED NUMERIC OPERATIONS
# ============================================================================

def round_decimal(v: Any, decimals: int = 2, **kwargs) -> Any:
    """Round number to specified decimal places."""
    try:
        return round(float(v), decimals)
    except (ValueError, TypeError):
        return v


def absolute_value(v: Any, **kwargs) -> Any:
    """Get absolute value of number."""
    try:
        return abs(float(v))
    except (ValueError, TypeError):
        return v


def ceiling(v: Any, **kwargs) -> Any:
    """Round up to nearest integer."""
    try:
        return math.ceil(float(v))
    except (ValueError, TypeError):
        return v


def floor(v: Any, **kwargs) -> Any:
    """Round down to nearest integer."""
    try:
        return math.floor(float(v))
    except (ValueError, TypeError):
        return v


def square_root(v: Any, **kwargs) -> Any:
    """Calculate square root."""
    try:
        return math.sqrt(float(v))
    except (ValueError, TypeError):
        return v


def power(v: Any, exponent: float = 2, **kwargs) -> Any:
    """Raise number to power."""
    try:
        return math.pow(float(v), exponent)
    except (ValueError, TypeError):
        return v


def modulo(v: Any, divisor: float = 10, **kwargs) -> Any:
    """Get remainder after division."""
    try:
        return float(v) % divisor
    except (ValueError, TypeError):
        return v


def clamp(v: Any, min_val: float = 0, max_val: float = 100, **kwargs) -> Any:
    """Clamp value between min and max."""
    try:
        num = float(v)
        return max(min_val, min(num, max_val))
    except (ValueError, TypeError):
        return v


def scale(v: Any, factor: float = 1.0, **kwargs) -> Any:
    """Scale number by factor."""
    try:
        return float(v) * factor
    except (ValueError, TypeError):
        return v


def reciprocal(v: Any, **kwargs) -> Any:
    """Calculate reciprocal (1/x)."""
    try:
        num = float(v)
        return 1.0 / num if num != 0 else None
    except (ValueError, TypeError, ZeroDivisionError):
        return None


# ============================================================================
# DATE/TIME OPERATIONS
# ============================================================================

def format_date(v: Any, format_string: str = '%Y-%m-%d', **kwargs) -> Any:
    """Format date to specific string format."""
    if isinstance(v, datetime):
        return v.strftime(format_string)
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.strftime(format_string)
        except:
            return v
    return v


def add_days(v: Any, days: int = 0, **kwargs) -> Any:
    """Add days to date."""
    if isinstance(v, datetime):
        return v + timedelta(days=days)
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt + timedelta(days=days)
        except:
            return v
    return v


def subtract_days(v: Any, days: int = 0, **kwargs) -> Any:
    """Subtract days from date."""
    return add_days(v, days=-days)


def day_of_week(v: Any, **kwargs) -> Any:
    """Get day of week (Monday=0, Sunday=6)."""
    if isinstance(v, datetime):
        return v.weekday()
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.weekday()
        except:
            return None
    return None


def day_name(v: Any, **kwargs) -> Any:
    """Get day name (Monday, Tuesday, etc.)."""
    if isinstance(v, datetime):
        return v.strftime('%A')
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.strftime('%A')
        except:
            return v
    return v


def month_name(v: Any, **kwargs) -> Any:
    """Get month name (January, February, etc.)."""
    if isinstance(v, datetime):
        return v.strftime('%B')
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.strftime('%B')
        except:
            return v
    return v


def year(v: Any, **kwargs) -> Any:
    """Extract year from date."""
    if isinstance(v, datetime):
        return v.year
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.year
        except:
            return None
    return None


def month(v: Any, **kwargs) -> Any:
    """Extract month from date."""
    if isinstance(v, datetime):
        return v.month
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.month
        except:
            return None
    return None


def day(v: Any, **kwargs) -> Any:
    """Extract day from date."""
    if isinstance(v, datetime):
        return v.day
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.day
        except:
            return None
    return None


# ============================================================================
# ARRAY/LIST OPERATIONS
# ============================================================================

def list_length(v: Any, **kwargs) -> Any:
    """Get length of list."""
    if isinstance(v, (list, tuple)):
        return len(v)
    return 0


def list_first(v: Any, **kwargs) -> Any:
    """Get first element of list."""
    if isinstance(v, (list, tuple)) and len(v) > 0:
        return v[0]
    return None


def list_last(v: Any, **kwargs) -> Any:
    """Get last element of list."""
    if isinstance(v, (list, tuple)) and len(v) > 0:
        return v[-1]
    return None


def list_unique(v: Any, **kwargs) -> Any:
    """Get unique elements from list."""
    if isinstance(v, list):
        return list(dict.fromkeys(v))  # Preserves order
    return v


def list_sort(v: Any, reverse: bool = False, **kwargs) -> Any:
    """Sort list."""
    if isinstance(v, list):
        try:
            return sorted(v, reverse=reverse)
        except:
            return v
    return v


# ============================================================================
# CONDITIONAL/LOGICAL OPERATIONS
# ============================================================================

def if_empty(v: Any, default: Any = '', **kwargs) -> Any:
    """Return default if value is empty."""
    if v is None or v == '':
        return default
    return v


def if_null(v: Any, default: Any = '', **kwargs) -> Any:
    """Return default if value is null."""
    if v is None:
        return default
    return v


def coalesce(v: Any, *alternatives, **kwargs) -> Any:
    """Return first non-null value."""
    if v is not None:
        return v
    for alt in alternatives:
        if alt is not None:
            return alt
    return None
