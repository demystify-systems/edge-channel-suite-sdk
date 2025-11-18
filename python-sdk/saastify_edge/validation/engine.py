"""
Validation Engine

Applies validation rules to transformed data.
"""

from typing import Dict, List, Any, Optional, Tuple
from ..core.types import ValidationRule, ValidationError
from .rules import VALIDATION_RULES


def validate_field(
    field_name: str,
    value: Any,
    rules: List[ValidationRule],
    context: Optional[Dict[str, Any]] = None
) -> List[ValidationError]:
    """
    Validate a single field against multiple rules.
    
    Args:
        field_name: Name of the field being validated
        value: The field value
        rules: List of validation rules to apply
        context: Optional context (full row data for cross-field validation)
    
    Returns:
        List of validation errors (empty if all validations pass)
    """
    errors: List[ValidationError] = []
    
    for rule in rules:
        rule_name = rule.get("rule")
        rule_args = rule.get("args", {})
        
        if rule_name not in VALIDATION_RULES:
            errors.append({
                "field": field_name,
                "rule": rule_name,
                "message": f"Unknown validation rule: {rule_name}",
                "value": value
            })
            continue
        
        validator = VALIDATION_RULES[rule_name]
        error_message = validator(value, rule_args, context)
        
        if error_message:
            errors.append({
                "field": field_name,
                "rule": rule_name,
                "message": error_message,
                "value": value
            })
    
    return errors


def validate_row(
    row_data: Dict[str, Any],
    field_validations: Dict[str, List[ValidationRule]]
) -> Tuple[bool, Dict[str, List[ValidationError]], int]:
    """
    Validate an entire row of data.
    
    Args:
        row_data: Dictionary of field names to values
        field_validations: Dictionary mapping field names to their validation rules
    
    Returns:
        Tuple of (is_valid, validation_errors_by_field, error_count)
    """
    all_errors: Dict[str, List[ValidationError]] = {}
    error_count = 0
    
    for field_name, rules in field_validations.items():
        if not rules:
            continue
        
        value = row_data.get(field_name)
        field_errors = validate_field(field_name, value, rules, row_data)
        
        if field_errors:
            all_errors[field_name] = field_errors
            error_count += len(field_errors)
    
    is_valid = error_count == 0
    
    return is_valid, all_errors, error_count


def validate_batch(
    rows: List[Dict[str, Any]],
    field_validations: Dict[str, List[ValidationRule]]
) -> List[Tuple[bool, Dict[str, List[ValidationError]], int]]:
    """
    Validate a batch of rows.
    
    Args:
        rows: List of row data dictionaries
        field_validations: Dictionary mapping field names to their validation rules
    
    Returns:
        List of (is_valid, validation_errors, error_count) tuples for each row
    """
    results = []
    
    for row in rows:
        result = validate_row(row, field_validations)
        results.append(result)
    
    return results
