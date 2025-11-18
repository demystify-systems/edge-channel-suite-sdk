"""
Transformation Engine

Executes transformation pipelines by applying a sequence of operations to values.
Supports both structured pipeline definitions and DSL string format.
"""

import re
from typing import Any, List, Dict, Optional, Tuple, Callable
from ..core.types import TransformationStep, RejectRow
from . import operations
from . import advanced_operations as adv


# Build the transformation registry - ALL 85 OPERATIONS
TRANSFORMS: Dict[str, Callable] = {
    # Core text operations (14)
    "uppercase": operations.uppercase,
    "lowercase": operations.lowercase,
    "strip": operations.strip,
    "title_case": operations.title_case,
    "capitalize": operations.capitalize,
    "split_comma": operations.split_comma,
    "split": operations.split,
    "join": operations.join,
    "replace": operations.replace,
    "replace_regex": operations.replace_regex,
    "prefix": operations.prefix,
    "suffix": operations.suffix,
    "clean_html": operations.clean_html,
    "clean_upc": operations.clean_upc,
    
    # Core numeric operations (8)
    "clean_numeric_value": operations.clean_numeric_value,
    "addition": operations.addition,
    "subtraction": operations.subtraction,
    "multiplication": operations.multiplication,
    "division": operations.division,
    "percentage": operations.percentage,
    "adjust_negative_to_zero": operations.adjust_negative_to_zero,
    "zero_padding": operations.zero_padding,
    
    # Core date operations (1)
    "date_only": operations.date_only,
    
    # Core control operations (4)
    "set": operations.set_value,
    "set_number": operations.set_number,
    "copy": operations.copy,
    "rejects": operations.rejects,
    
    # Core lookup operations (1)
    "vlookup_map": operations.vlookup_map,
    
    # Advanced text operations (19)
    "remove_whitespace": adv.remove_whitespace,
    "truncate": adv.truncate,
    "pad_left": adv.pad_left,
    "pad_right": adv.pad_right,
    "slugify": adv.slugify,
    "extract_numbers": adv.extract_numbers,
    "extract_letters": adv.extract_letters,
    "reverse_string": adv.reverse_string,
    "word_count": adv.word_count,
    "char_count": adv.char_count,
    "to_snake_case": adv.to_snake_case,
    "to_camel_case": adv.to_camel_case,
    "to_pascal_case": adv.to_pascal_case,
    "remove_accents": adv.remove_accents,
    "title_case_all_words": adv.title_case_all_words,
    "sanitize_filename": adv.sanitize_filename,
    "string_similarity": adv.string_similarity,
    "levenshtein_distance": adv.levenshtein_distance,
    "phonetic_match": adv.phonetic_match,
    
    # Advanced numeric operations (7)
    "round_decimal": adv.round_decimal,
    "absolute_value": adv.absolute_value,
    "ceiling": adv.ceiling,
    "floor": adv.floor,
    "clamp": adv.clamp,
    "scale": adv.scale,
    "modulo": adv.modulo,
    
    # Advanced date operations (11)
    "format_date": adv.format_date,
    "add_days": adv.add_days,
    "subtract_days": adv.subtract_days,
    "day_of_week": adv.day_of_week,
    "day_name": adv.day_name,
    "month_name": adv.month_name,
    "year": adv.year,
    "month": adv.month,
    "day": adv.day,
    "is_weekend": adv.is_weekend,
    "days_between": adv.days_between,
    
    # Advanced list operations (5)
    "list_length": adv.list_length,
    "list_first": adv.list_first,
    "list_last": adv.list_last,
    "list_unique": adv.list_unique,
    "list_sort": adv.list_sort,
    
    # Advanced conditional operations (3)
    "if_empty": adv.if_empty,
    "if_null": adv.if_null,
    "coalesce": adv.coalesce,
    
    # Advanced utility operations (3)
    "url_encode": adv.url_encode,
    "url_decode": adv.url_decode,
    "extract_domain": adv.extract_domain,
}


def apply_transformations(
    val: Any,
    steps: List[TransformationStep],
    context: Optional[Dict[str, Any]] = None
) -> Tuple[Any, bool]:
    """
    Apply a sequence of transformation steps to a value.
    
    Args:
        val: The input value
        steps: List of transformation steps with name and params
        context: Optional context (full row data, template info, etc.)
    
    Returns:
        Tuple of (transformed_value, is_rejected)
    """
    v = val
    
    for step in steps:
        func_name = step.get("name")
        if func_name not in TRANSFORMS:
            raise ValueError(f"Unknown transformation: {func_name}")
        
        func = TRANSFORMS[func_name]
        params = step.get("params", {})
        
        try:
            v = func(v, **params)
        except RejectRow:
            return None, True
        except Exception as e:
            # Log error but continue with original value
            print(f"Transformation error in {func_name}: {e}")
            continue
    
    return v, False


def transform(value: Any, rule_string: str) -> Any:
    """
    Apply DSL transformation rule to a single value (convenience function).
    
    Args:
        value: Input value to transform
        rule_string: DSL rule string (e.g., "strip + uppercase")
        
    Returns:
        Transformed value
        
    Example:
        >>> transform("  hello  ", "strip + uppercase")
        'HELLO'
    """
    results = bulk_apply_pipe_rules([value], rule_string)
    return results[0] if results else None


def bulk_apply_pipe_rules(
    values_list: List[Any],
    rule_strings: Any
) -> List[Any]:
    """
    Apply DSL transformation rules to a list of values.
    
    Supports broadcasting:
    - Single rule → multiple values
    - Multiple rules → single value  
    - Equal length arrays
    
    DSL Syntax:
    - Chain operations with ' + ' (spaces required)
    - Parameterize with '|': operation|param1|param2
    - Special delimiters:
      - split||| or split|\\| → split by pipe character
      - split|| → split by space
      - join|, → join with comma
    - vlookup|key1:val1,key2:val2
    - Arithmetic: addition|5, multiplication|2.5
    
    Args:
        values_list: List of values to transform
        rule_strings: String rule or list of rules
    
    Returns:
        List of transformed values
    """
    if not isinstance(values_list, list):
        raise ValueError("values_list must be a list")
    
    # Broadcasting logic
    if isinstance(rule_strings, str):
        rule_strings = [rule_strings] * len(values_list)
    elif isinstance(rule_strings, list):
        if len(rule_strings) == 1 and len(values_list) > 1:
            rule_strings *= len(values_list)
        elif len(values_list) == 1 and len(rule_strings) > 1:
            values_list *= len(rule_strings)
        elif len(rule_strings) != len(values_list):
            raise ValueError("Length mismatch between values_list and rule_strings")
    else:
        raise ValueError("rule_strings must be str or list[str]")
    
    results = []
    
    for val, rule in zip(values_list, rule_strings):
        if not rule:
            results.append(val)
            continue
        
        steps = _parse_dsl_rule(rule)
        out, _ = apply_transformations(val, steps)
        results.append(out)
    
    return results


def _parse_dsl_rule(rule: str) -> List[TransformationStep]:
    """
    Parse a DSL rule string into transformation steps.
    
    Args:
        rule: DSL rule string (e.g., "uppercase + strip + replace|old|new")
    
    Returns:
        List of TransformationStep dictionaries
    """
    steps: List[TransformationStep] = []
    
    # Split by ' + ' to get individual operations
    tokens = rule.replace(' + ', '|;|').split('|;|')
    
    for token_raw in tokens:
        token = token_raw.lstrip()
        if not token:
            continue
        
        # ─── Handle split operation ───
        if token.startswith("split|"):
            raw = token[6:]
            
            # Handle special delimiter cases
            if raw in ("||", r"\|"):
                delim = "|"
            elif raw.startswith("|||"):
                delim = raw[3:] or "|"
            elif raw.startswith("||"):
                tail = raw[2:]
                delim = " " if tail in ("", " ") else tail
            elif raw.startswith(r"\|"):
                delim = "|" + raw[2:]
            else:
                delim = raw
            
            if delim != " ":
                delim = delim.strip()
            if delim == "":
                raise ValueError("split requires non-empty delimiter")
            
            steps.append({"name": "split", "params": {"delimiter": delim}})
            continue
        
        # ─── Handle join operation ───
        if token.startswith("join|"):
            steps.append({"name": "join", "params": {"delimiter": token[5:]}})
            continue
        
        # ─── Handle prefix operation ───
        if token.startswith("prefix|"):
            steps.append({"name": "prefix", "params": {"prefix_str": token[7:]}})
            continue
        
        # ─── Handle suffix operation ───
        if token.startswith("suffix|"):
            steps.append({"name": "suffix", "params": {"suffix_str": token[7:]}})
            continue
        
        # ─── Handle replace_regex operation ───
        if token.startswith("replace_regex|"):
            parts = token[14:].split("||", 1)
            pat = parts[0]
            rep = parts[1] if len(parts) > 1 else ""
            steps.append({"name": "replace_regex", "params": {"pattern": pat, "repl": rep}})
            continue
        
        # ─── Handle replace operation ───
        if token.startswith("replace|"):
            try:
                old, new = token[8:].split('|', 1)
                steps.append({"name": "replace", "params": {"old": old, "new": new}})
            except ValueError:
                raise ValueError(f"replace requires two parameters: {token}")
            continue
        
        # ─── Handle vlookup operation ───
        if token.startswith("vlookup|"):
            mapping = {}
            for pair in token[8:].rstrip('|').split(','):
                k, v = pair.split(':', 1)
                v = v.strip()
                # Type coercion for values
                if v.lower() == "true":
                    v = True
                elif v.lower() == "false":
                    v = False
                elif re.match(r'^-?\d+\.\d+$', v):
                    v = float(v)
                elif v.isdigit():
                    v = int(v)
                
                mapping[k.strip().lower()] = v
            
            steps.append({"name": "vlookup_map", "params": {"mapping": mapping}})
            continue
        
        # ─── Handle arithmetic operations ───
        arithmetic_ops = {
            "addition": "amount",
            "subtraction": "amount",
            "multiplication": "factor",
            "division": "divisor",
            "percentage": "factor"
        }
        
        handled = False
        for op, param_name in arithmetic_ops.items():
            if token.startswith(f"{op}|"):
                param_value = token.split('|', 1)[1]
                steps.append({"name": op, "params": {param_name: param_value}})
                handled = True
                break
        
        if handled:
            continue
        
        # ─── Handle parameterized operations ───
        if token.startswith("strip|"):
            steps.append({"name": "strip", "params": {"chars": token.split('|', 1)[1]}})
        elif token.startswith("set|"):
            steps.append({"name": "set", "params": {"value": token.split('|', 1)[1]}})
        elif token.startswith("set_number|"):
            steps.append({"name": "set_number", "params": {"value": token.split('|', 1)[1]}})
        elif token.startswith("zero_padding|"):
            steps.append({"name": "zero_padding", "params": {"value": token.split('|', 1)[1]}})
        elif token == "rejects":
            steps.append({"name": "rejects"})
        else:
            # Simple operation without parameters
            steps.append({"name": token})
    
    return steps
