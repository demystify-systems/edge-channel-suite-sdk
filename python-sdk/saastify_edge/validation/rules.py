"""
Validation rules implementation

Each validation function takes a value, args, and optional context.
Returns None if valid, or an error message if invalid.
"""

import re
from datetime import datetime
from typing import Any, Optional, Dict, List


def required(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Value must be present and non-empty"""
    if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
        return "Field is required"
    return None


def regex(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Value must match a regex pattern"""
    if value is None or value == "":
        return None  # Skip validation for empty values (use 'required' for that)
    
    pattern = args.get("pattern")
    flags_str = args.get("flags", "")
    
    if not pattern:
        return "Regex pattern not specified"
    
    # Parse regex flags
    flags = 0
    if "i" in flags_str.lower():
        flags |= re.IGNORECASE
    if "m" in flags_str.lower():
        flags |= re.MULTILINE
    if "s" in flags_str.lower():
        flags |= re.DOTALL
    
    try:
        if not re.match(pattern, str(value), flags):
            return f"Value does not match pattern: {pattern}"
    except re.error as e:
        return f"Invalid regex pattern: {e}"
    
    return None


def enum(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Value must be one of allowed values"""
    if value is None or value == "":
        return None
    
    allowed_values = args.get("values", [])
    if not allowed_values:
        return "No allowed values specified"
    
    if value not in allowed_values:
        return f"Value must be one of: {', '.join(map(str, allowed_values))}"
    
    return None


def min_length(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """String length must be at least min value"""
    if value is None or value == "":
        return None
    
    min_len = args.get("value")
    if min_len is None:
        return "Minimum length not specified"
    
    if len(str(value)) < min_len:
        return f"Value must be at least {min_len} characters long"
    
    return None


def max_length(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """String length must not exceed max value"""
    if value is None or value == "":
        return None
    
    max_len = args.get("value")
    if max_len is None:
        return "Maximum length not specified"
    
    if len(str(value)) > max_len:
        return f"Value must not exceed {max_len} characters"
    
    return None


def numeric_range(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Number must fall within min/max range"""
    if value is None or value == "":
        return None
    
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return "Value must be numeric"
    
    min_val = args.get("min")
    max_val = args.get("max")
    
    if min_val is not None and num_value < min_val:
        return f"Value must be at least {min_val}"
    
    if max_val is not None and num_value > max_val:
        return f"Value must not exceed {max_val}"
    
    return None


def date_before(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Date must be before given date or field"""
    if value is None or value == "":
        return None
    
    try:
        if isinstance(value, str):
            value_date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif isinstance(value, datetime):
            value_date = value
        else:
            return "Value must be a valid date"
    except (ValueError, AttributeError):
        return "Invalid date format"
    
    # Check against fixed date
    compare_date_str = args.get("date")
    if compare_date_str:
        try:
            compare_date = datetime.fromisoformat(compare_date_str.replace("Z", "+00:00"))
            if value_date >= compare_date:
                return f"Date must be before {compare_date_str}"
        except ValueError:
            return f"Invalid comparison date: {compare_date_str}"
    
    # Check against another field
    field_name = args.get("field")
    if field_name and context:
        compare_value = context.get(field_name)
        if compare_value:
            try:
                if isinstance(compare_value, str):
                    compare_date = datetime.fromisoformat(compare_value.replace("Z", "+00:00"))
                elif isinstance(compare_value, datetime):
                    compare_date = compare_value
                else:
                    return f"Field {field_name} is not a valid date"
                
                if value_date >= compare_date:
                    return f"Date must be before {field_name}"
            except ValueError:
                return f"Invalid date in field {field_name}"
    
    return None


def date_after(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Date must be after given date or field"""
    if value is None or value == "":
        return None
    
    try:
        if isinstance(value, str):
            value_date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif isinstance(value, datetime):
            value_date = value
        else:
            return "Value must be a valid date"
    except (ValueError, AttributeError):
        return "Invalid date format"
    
    # Check against fixed date
    compare_date_str = args.get("date")
    if compare_date_str:
        try:
            compare_date = datetime.fromisoformat(compare_date_str.replace("Z", "+00:00"))
            if value_date <= compare_date:
                return f"Date must be after {compare_date_str}"
        except ValueError:
            return f"Invalid comparison date: {compare_date_str}"
    
    # Check against another field
    field_name = args.get("field")
    if field_name and context:
        compare_value = context.get(field_name)
        if compare_value:
            try:
                if isinstance(compare_value, str):
                    compare_date = datetime.fromisoformat(compare_value.replace("Z", "+00:00"))
                elif isinstance(compare_value, datetime):
                    compare_date = compare_value
                else:
                    return f"Field {field_name} is not a valid date"
                
                if value_date <= compare_date:
                    return f"Date must be after {field_name}"
            except ValueError:
                return f"Invalid date in field {field_name}"
    
    return None


def custom_expression(value: Any, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Evaluate arbitrary expression referencing fields"""
    if not context:
        return "Context required for custom expression"
    
    expression = args.get("expression")
    if not expression:
        return "Expression not specified"
    
    try:
        # Create a safe evaluation context with field values
        eval_context = context.copy()
        eval_context["value"] = value
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, eval_context)
        
        if not result:
            return f"Expression failed: {expression}"
    except Exception as e:
        return f"Expression error: {e}"
    
    return None


# Validation rules registry
VALIDATION_RULES = {
    "required": required,
    "regex": regex,
    "enum": enum,
    "min_length": min_length,
    "max_length": max_length,
    "numeric_range": numeric_range,
    "date_before": date_before,
    "date_after": date_after,
    "custom_expression": custom_expression,
}
