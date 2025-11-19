"""
Advanced Transformation Operations

Additional 40+ transformation operations for extended functionality.
"""

import re
import math
from typing import Any, Optional, Dict
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


def lstrip(v: Any, chars: Optional[str] = None, **kwargs) -> Any:
    """Trim whitespace (or specified chars) from the left end."""
    if not isinstance(v, str):
        return v
    return v.lstrip(chars) if chars else v.lstrip()


def strip_extra_spaces(v: Any, **kwargs) -> Any:
    """Collapse multiple spaces into one."""
    if not isinstance(v, str):
        return v
    return re.sub(r'\s+', ' ', v).strip()


def remove_non_ascii(v: Any, **kwargs) -> Any:
    """Remove non-ASCII characters."""
    if not isinstance(v, str):
        return v
    return v.encode('ascii', 'ignore').decode('ascii')


def remove_emojis(v: Any, **kwargs) -> Any:
    """Remove all emoji characters."""
    if not isinstance(v, str):
        return v
    # Emoji pattern - covers most emoji ranges
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
    return emoji_pattern.sub('', v)


def strip_quotes(v: Any, **kwargs) -> Any:
    """Remove leading/trailing single or double quotes."""
    if not isinstance(v, str):
        return v
    return v.strip("'\"") if v.startswith(("'", '"')) and v.endswith(("'", '"')) else v


def substring(v: Any, start_index: int, length: Optional[int] = None, **kwargs) -> Any:
    """Extract a substring given start index and optional length."""
    if not isinstance(v, str):
        return v
    if length is None:
        return v[start_index:]
    return v[start_index:start_index + length]


def extract_alphanumeric(v: Any, **kwargs) -> Any:
    """Extract only alphanumeric characters."""
    if not isinstance(v, str):
        return v
    return ''.join(re.findall(r'[a-zA-Z0-9]', v))


def extract_regex(v: Any, pattern: str, group_index: int = 0, **kwargs) -> Any:
    """Extract a regex group from string."""
    if not isinstance(v, str):
        return v
    match = re.search(pattern, v)
    if match:
        if group_index == 0:
            return match.group(0)
        return match.group(group_index) if match.lastindex and group_index <= match.lastindex else None
    return None


def normalize_whitespace(v: Any, **kwargs) -> Any:
    """Replace tabs/newlines with spaces then collapse spaces."""
    if not isinstance(v, str):
        return v
    # Replace tabs and newlines with spaces
    v = re.sub(r'[\t\n\r]+', ' ', v)
    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', v).strip()


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


def add_months(v: Any, months: int = 0, **kwargs) -> Any:
    """Add months to a date."""
    if isinstance(v, datetime):
        # Calculate new month and year
        new_month = v.month + months
        new_year = v.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
        try:
            return v.replace(year=new_year, month=new_month)
        except ValueError:
            # Day doesn't exist in target month, use last day of month
            from calendar import monthrange
            last_day = monthrange(new_year, new_month)[1]
            return v.replace(year=new_year, month=new_month, day=min(v.day, last_day))
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            result = add_months(dt, months)
            return result.isoformat()
        except:
            return v
    return v


def date_diff_days(v: Any, start_field: Optional[str] = None, end_field: Optional[str] = None, 
                   context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Compute difference in days between two dates."""
    if not context:
        return v
    
    # If start_field and end_field provided, use them
    if start_field and end_field:
        start_date = context.get(start_field)
        end_date = context.get(end_field) if end_field else v
    else:
        # Use value as one date and context for the other
        start_date = v
        end_date = context.get('_end_date') if '_end_date' in context else None
    
    if not start_date or not end_date:
        return None
    
    # Parse dates
    def parse_date(d):
        if isinstance(d, datetime):
            return d
        if isinstance(d, str):
            try:
                return datetime.fromisoformat(d.replace('Z', '+00:00'))
            except:
                return None
        return None
    
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if start_dt and end_dt:
        delta = end_dt - start_dt
        return delta.days
    
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


def list_limit(v: Any, max_items: int = 10, **kwargs) -> Any:
    """Limit list to first N items."""
    if isinstance(v, list):
        return v[:max_items]
    return v


def list_filter_regex(v: Any, pattern: str, **kwargs) -> Any:
    """Filter list items by regex pattern."""
    if not isinstance(v, list):
        return v
    try:
        regex_pattern = re.compile(pattern)
        return [item for item in v if regex_pattern.search(str(item))]
    except re.error:
        return v


def list_join_with_and(v: Any, **kwargs) -> Any:
    """Join list into human-friendly string with commas and 'and'."""
    if not isinstance(v, list):
        return v
    if not v:
        return ""
    if len(v) == 1:
        return str(v[0])
    if len(v) == 2:
        return f"{v[0]} and {v[1]}"
    return ", ".join(str(x) for x in v[:-1]) + f", and {v[-1]}"


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


# ============================================================================
# FIELD OPERATIONS (Context-aware)
# ============================================================================

def addition_fields(v: Any, fields: Optional[list] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Sum multiple fields in record."""
    if not context or not fields:
        return v
    try:
        total = 0.0
        for field in fields:
            field_value = context.get(field)
            if field_value is not None:
                total += float(field_value)
        return total
    except (ValueError, TypeError):
        return v


def diff_fields(v: Any, minuend: Optional[str] = None, subtrahend: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Subtract one field from another."""
    if not context or not minuend or not subtrahend:
        return v
    try:
        minuend_val = float(context.get(minuend, 0))
        subtrahend_val = float(context.get(subtrahend, 0))
        return minuend_val - subtrahend_val
    except (ValueError, TypeError):
        return v


def prod_fields(v: Any, fields: Optional[list] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Multiply multiple fields."""
    if not context or not fields:
        return v
    try:
        product = 1.0
        for field in fields:
            field_value = context.get(field)
            if field_value is not None:
                product *= float(field_value)
        return product
    except (ValueError, TypeError):
        return v


def ratio_fields(v: Any, numerator: Optional[str] = None, denominator: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Divide one field by another."""
    if not context or not numerator or not denominator:
        return v
    try:
        num_val = float(context.get(numerator, 0))
        den_val = float(context.get(denominator, 0))
        if den_val == 0:
            return None
        return num_val / den_val
    except (ValueError, TypeError):
        return v


def concat(v: Any, fields: Optional[list] = None, delimiter: str = " ", 
          context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Concatenate multiple fields with delimiter."""
    if not context or not fields:
        return v
    values = []
    for field in fields:
        field_value = context.get(field)
        if field_value is not None:
            values.append(str(field_value))
    return delimiter.join(values)


def field_copy_from(v: Any, source_field: Optional[str] = None, 
                   context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """Copy value of another field."""
    if not context or not source_field:
        return v
    return context.get(source_field, v)


# ============================================================================
# LOOKUP OPERATIONS
# ============================================================================

def lookup_category_path(v: Any, category_id_field: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None, 
                        db_client: Optional[Any] = None, **kwargs) -> Any:
    """
    Resolve category ID to its full path.
    
    Requires db_client with category lookup capability.
    Example: "123" → "Electronics > Mobile > Smartphones"
    """
    if not context or not db_client:
        return v
    
    category_id = context.get(category_id_field) if category_id_field else v
    if not category_id:
        return v
    
    # In production, this would query the database for category hierarchy
    # For now, return a placeholder that indicates the operation is available
    # The actual implementation would depend on the database schema
    try:
        # Placeholder: would query category table via db_client
        # category_path = await db_client.get_category_path(category_id)
        # return category_path
        return f"Category_{category_id}"  # Placeholder
    except Exception:
        return v


def lookup_uom_conversion(v: Any, from_unit: Optional[str] = None, to_unit: Optional[str] = None,
                         value: Optional[float] = None, context: Optional[Dict[str, Any]] = None,
                         db_client: Optional[Any] = None, **kwargs) -> Any:
    """
    Convert units of measure via mapping.
    
    Requires db_client with UOM conversion table.
    Example: Convert 100 "kg" to "lbs" → 220.46
    """
    if not context or not db_client:
        return v
    
    from_uom = from_unit or context.get('unit', '')
    to_uom = to_unit or context.get('target_unit', '')
    val = float(value) if value is not None else float(v) if v else 0.0
    
    if not from_uom or not to_uom:
        return v
    
    # In production, this would query the UOM conversion table
    # For now, return a placeholder
    try:
        # conversion_factor = await db_client.get_uom_conversion(from_uom, to_uom)
        # return val * conversion_factor
        return val  # Placeholder - would multiply by conversion factor
    except Exception:
        return v
