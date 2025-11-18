"""
Transformation operations

Each function takes a value and keyword arguments and returns a transformed value.
Functions should be pure and handle type mismatches gracefully.
"""

import re
from datetime import datetime, date
from typing import Any, Optional, List, Union, Dict
from ..core.types import RejectRow


# ─── Text Operations ────────────────────────────────────────────────────────

def uppercase(v: Any, **kw) -> Any:
    """Convert string to upper case"""
    return v.upper() if isinstance(v, str) else v


def lowercase(v: Any, **kw) -> Any:
    """Convert string to lower case"""
    return v.lower() if isinstance(v, str) else v


def strip(v: Any, chars: Optional[str] = None, **kw) -> Any:
    """Trim whitespace (or specified chars) from both ends"""
    return v.strip(chars) if isinstance(v, str) else v


def title_case(v: Any, **kw) -> Any:
    """Capitalize the first letter of each word"""
    return v.title() if isinstance(v, str) else v


def capitalize(v: Any, **kw) -> Any:
    """Capitalize only the first letter of the string"""
    return v.capitalize() if isinstance(v, str) else v


def split_comma(v: Any, **kw) -> Any:
    """Split string by comma and strip each element"""
    if isinstance(v, str):
        return [x.strip() for x in v.split(',')]
    return v


def split(v: Any, delimiter: str, **kw) -> Any:
    """Split string into list by delimiter"""
    return v.split(delimiter) if isinstance(v, str) else v


def join(v: Any, delimiter: str, **kw) -> Any:
    """Join list of values into string with delimiter"""
    if isinstance(v, str):
        v = v.split()
    return delimiter.join(str(x) for x in v) if isinstance(v, (list, tuple)) else v


def replace(v: Any, old: str, new: str, **kw) -> Any:
    """Replace all occurrences of a substring"""
    return v.replace(old, new) if isinstance(v, str) else v


def replace_regex(v: Any, pattern: str, repl: str, **kw) -> Any:
    """Replace occurrences based on a regex pattern"""
    return re.sub(pattern, repl, v) if isinstance(v, str) else v


def prefix(v: Any, prefix_str: str = "-", **kw) -> Any:
    """Prepend a string"""
    if isinstance(v, (list, tuple)):
        return [prefix_str + str(x) for x in v]
    if isinstance(v, str):
        return prefix_str + v
    return v


def suffix(v: Any, suffix_str: str = "_", **kw) -> Any:
    """Append a string"""
    if isinstance(v, (list, tuple)):
        return [str(x) + suffix_str for x in v]
    if isinstance(v, str):
        return v + suffix_str
    return v


def clean_html(v: Any, **kw) -> Any:
    """Remove HTML tags"""
    return re.sub(r'<.*?>', '', v) if isinstance(v, str) else v


def clean_upc(v: Any, **kw) -> Any:
    """Remove non-numeric characters from UPC"""
    return re.sub(r'[^\d]', '', v) if isinstance(v, str) else v


# ─── Numeric Operations ─────────────────────────────────────────────────────

def clean_numeric_value(v: Any, **kw) -> Any:
    """Remove non-numeric characters from text and parse number"""
    if isinstance(v, str):
        try:
            return float(re.sub(r'[^\d.]', '', v))
        except ValueError:
            return v
    return v


def addition(v: Any, amount: Union[int, float], **kw) -> Any:
    """Add a constant to numeric value"""
    try:
        return float(v) + float(amount)
    except (ValueError, TypeError):
        return v


def subtraction(v: Any, amount: Union[int, float], **kw) -> Any:
    """Subtract from numeric value"""
    try:
        return float(v) - float(amount)
    except (ValueError, TypeError):
        return v


def multiplication(v: Any, factor: Union[int, float], **kw) -> Any:
    """Multiply numeric value"""
    try:
        return float(v) * float(factor)
    except (ValueError, TypeError):
        return v


def division(v: Any, divisor: Union[int, float], **kw) -> Any:
    """Divide numeric value (returns None if divisor is zero)"""
    try:
        divisor_float = float(divisor)
        if divisor_float == 0:
            return None
        return float(v) / divisor_float
    except (ValueError, TypeError):
        return v


def percentage(v: Any, factor: Union[int, float] = 100, **kw) -> Any:
    """Calculate percentage of a number"""
    try:
        return float(v) * float(factor)
    except (ValueError, TypeError):
        return v


def adjust_negative_to_zero(v: Any, **kw) -> Any:
    """Convert negative numbers to zero"""
    try:
        return max(0, float(v))
    except (ValueError, TypeError):
        return v


def zero_padding(v: Any, value: int, **kw) -> Any:
    """Pad number with leading zeros to specified length"""
    return str(v).zfill(int(value))


# ─── Date Operations ────────────────────────────────────────────────────────

def date_only(v: Any, **kw) -> Any:
    """Extract only the date portion (remove time)"""
    if isinstance(v, str):
        try:
            return datetime.strptime(v.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError:
            # Try to just extract date part if space exists
            return v.split()[0] if " " in v else v
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return v


# ─── Control Operations ─────────────────────────────────────────────────────

def set_value(v: Any, value: Any, **kw) -> Any:
    """Force value to a specific constant"""
    return value


def set_number(v: Any, value: Union[int, float], **kw) -> Any:
    """Force value to a specific number"""
    return int(value)


def copy(v: Any, **kw) -> Any:
    """Pass through value unchanged"""
    return v


def rejects(v: Any, **kw) -> None:
    """Mark row for rejection"""
    raise RejectRow()


# ─── Lookup Operations ──────────────────────────────────────────────────────

def vlookup_map(v: Any, mapping: Optional[Dict[str, Any]] = None, **kw) -> Any:
    """Map a value via a lookup table (case-insensitive)"""
    if isinstance(v, str) and mapping:
        return mapping.get(v.lower(), v)
    return v
