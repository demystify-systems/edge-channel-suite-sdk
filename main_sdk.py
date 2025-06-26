#transformation_export
import re
from datetime import datetime, date


# ─── Sentinel ───────────────────────────────────────────────────────────────
class RejectRow(Exception):
    pass

# ─── Transform helpers ──────────────────────────────────────────────────────
def uppercase(v, **kw): return v.upper() if isinstance(v, str) else v
def lowercase(v, **kw): return v.lower() if isinstance(v, str) else v
def strip(v, chars=None, **kw): return v.strip(chars) if isinstance(v, str) else v
def title_case(v, **kw): return v.title() if isinstance(v, str) else v
def capitalize(v, **kw): return v.capitalize() if isinstance(v, str) else v
def split_comma(v, **kw): return [x.strip() for x in v.split(',')] if isinstance(v, str) else v
def split(v, delimiter, **kw): return v.split(delimiter) if isinstance(v, str) else v
def join(v, delimiter, **kw):
    if isinstance(v, str): v = v.split()
    return delimiter.join(str(x) for x in v) if isinstance(v, (list, tuple)) else v
def replace(v, old, new, **kw): return v.replace(old, new) if isinstance(v, str) else v
def replace_regex(v, pattern, repl, **kw): return re.sub(pattern, repl, v) if isinstance(v, str) else v
def clean_numeric_value(v, **kw): return float(re.sub(r'[^\d.]', '', v)) if isinstance(v, str) else v
def clean_upc(v, **kw): return re.sub(r'[^\d]', '', v) if isinstance(v, str) else v
def clean_html(v, **kw): return re.sub(r'<.*?>', '', v) if isinstance(v, str) else v
def date_only(v, **kw):
    if isinstance(v, str):
        try: return datetime.strptime(v.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError: return v.split()[0] if " " in v else v
    if isinstance(v, (datetime, date)): return v.strftime("%Y-%m-%d")
    return v
def set_value(v, value, **kw): return value
def set_number(v, value, **kw): return int(value)
def zero_padding(v, value, **kw): return str(v).zfill(int(value))
def addition(v, amount, **kw): return float(v) + float(amount)
def subtraction(v, amount, **kw): return float(v) - float(amount)
def multiplication(v, factor, **kw): return float(v) * float(factor)
def division(v, divisor, **kw): return float(v) / float(divisor) if float(divisor) != 0 else None
def percentage(v, factor=100, **kw): return float(v) * float(factor)
def adjust_negative_to_zero(v, **kw):
    try: return max(0, float(v))
    except: return v
def vlookup_map(v, mapping=None, **kw):
    if isinstance(v, str) and mapping: return mapping.get(v.lower(), v)
    return v
def prefix(v, prefix_str="-", **kw):
    if isinstance(v, (list, tuple)): return [prefix_str + str(x) for x in v]
    if isinstance(v, str): return prefix_str + v
    return v
def suffix(v, suffix_str="_", **kw):
    if isinstance(v, (list, tuple)): return [str(x) + suffix_str for x in v]
    if isinstance(v, str): return v + suffix_str
    return v
def copy(v, **kw): return v
def rejects(v, **kw): raise RejectRow()

# ─── Registry ───────────────────────────────────────────────────────────────
TRANSFORMS = {
    "uppercase": uppercase, "lowercase": lowercase, "strip": strip, "title_case": title_case,
    "capitalize": capitalize, "split_comma": split_comma, "split": split, "join": join,
    "replace": replace, "replace_regex": replace_regex, "clean_numeric_value": clean_numeric_value,
    "clean_upc": clean_upc, "clean_html": clean_html, "date_only": date_only,
    "set": set_value, "set_number": set_number, "zero_padding": zero_padding,
    "addition": addition, "subtraction": subtraction, "multiplication": multiplication,
    "division": division, "percentage": percentage, "adjust_negative_to_zero": adjust_negative_to_zero,
    "vlookup_map": vlookup_map, "prefix": prefix, "suffix": suffix,
    "copy": copy, "rejects": rejects
}

# ─── Run one pipeline ───────────────────────────────────────────────────────
def apply_transformations(val, steps):
    v = val
    for st in steps:
        func = TRANSFORMS[st["name"]]
        try: v = func(v, **st.get("params", {}))
        except RejectRow: return None, True
    return v, False

# ─── DSL engine with broadcasting ───────────────────────────────────────────
def bulk_apply_pipe_rules(values_list, rule_strings):
    if not isinstance(values_list, list):
        raise ValueError("values_list must be a list")

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

        steps = []
        for token_raw in rule.replace('+', '|;|').split('|;|'):
            token = token_raw.lstrip()
            if not token:
                continue

            # ---------- split ----------
            if token.startswith("split|"):
                raw = token[6:]
                if raw in ("|||", r"\|"):
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
                if delim != " ": delim = delim.strip()
                if delim == "": raise ValueError("split requires non-empty delimiter")
                steps.append({"name": "split", "params": {"delimiter": delim}})
                continue

            # ---------- join ----------
            if token.startswith("join|"):
                steps.append({"name": "join", "params": {"delimiter": token[5:]}})
                continue

            # ---------- prefix / suffix ----------
            if token.startswith("prefix|"):
                steps.append({"name": "prefix", "params": {"prefix_str": token[7:]}})
                continue
            if token.startswith("suffix|"):
                steps.append({"name": "suffix", "params": {"suffix_str": token[7:]}})
                continue

            # ---------- replace_regex ----------
            if token.startswith("replace_regex|"):
                pat, *rep = token[14:].split("||", 1)
                steps.append({"name": "replace_regex",
                              "params": {"pattern": pat, "repl": rep[0] if rep else ""}})
                continue

            # ---------- replace ----------
            if token.startswith("replace|"):
                try:
                    old, new = token[8:].split('|', 1)
                except ValueError:
                    raise ValueError(f"replace requires two parameters: {token}")
                steps.append({"name": "replace",
                              "params": {"old": old, "new": new}})
                continue

            # ---------- vlookup ----------
            if token.startswith("vlookup|"):
                mapping = {}
                for pair in token[8:].rstrip('|').split(','):
                    k, v = pair.split(':', 1)
                    v = v.strip()
                    mapping[k.strip().lower()] = \
                        True if v.lower() == "true" else \
                        False if v.lower() == "false" else \
                        float(v) if re.match(r'^-?\d+\.\d+$', v) else \
                        int(v) if v.isdigit() else v
                steps.append({"name": "vlookup_map", "params": {"mapping": mapping}})
                continue

            # ---------- arithmetic ----------
            for op in ("addition", "subtraction", "multiplication", "division", "percentage"):
                if token.startswith(f"{op}|"):
                    param = token.split('|', 1)[1]
                    key = ("amount" if op in ("addition", "subtraction") else
                           "factor" if op in ("multiplication", "percentage") else
                           "divisor")
                    steps.append({"name": op, "params": {key: param}})
                    break
            else:
                # ---------- strip with chars / set / zero_padding ----------
                if token.startswith("strip|"):
                    steps.append({"name": "strip",
                                  "params": {"chars": token.split('|',1)[1]}})
                elif token.startswith("set|"):
                    steps.append({"name": "set",
                                  "params": {"value": token.split('|',1)[1]}})
                elif token.startswith("set_number|"):
                    steps.append({"name": "set_number",
                                  "params": {"value": token.split('|',1)[1]}})
                elif token.startswith("zero_padding|"):
                    steps.append({"name": "zero_padding",
                                  "params": {"value": token.split('|',1)[1]}})
                elif token == "rejects":
                    steps.append({"name": "rejects"})
                else:
                    steps.append({"name": token})

        out, _ = apply_transformations(val, steps)
        results.append(out)

    return results