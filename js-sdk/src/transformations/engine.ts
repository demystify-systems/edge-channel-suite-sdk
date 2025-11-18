/**
 * Transformation Engine - DSL parser and executor
 * Modular, easy to extend and debug
 */

import { TransformationStep, TransformFn, RejectRow } from '../core/types';
import * as text from './text';
import * as string from './string';
import * as numeric from './numeric';
import * as date from './date';
import * as list from './list';
import * as conditional from './conditional';
import * as utility from './utility';

// Registry of all transformation functions
const TRANSFORMS: Record<string, TransformFn> = {
  // Text operations
  uppercase: text.uppercase,
  lowercase: text.lowercase,
  strip: text.strip,
  title_case: text.titleCase,
  capitalize: text.capitalize,
  remove_whitespace: text.removeWhitespace,
  truncate: text.truncate,
  pad_left: text.padLeft,
  pad_right: text.padRight,
  reverse_string: text.reverseString,
  word_count: text.wordCount,
  char_count: text.charCount,
  extract_numbers: text.extractNumbers,
  extract_letters: text.extractLetters,
  remove_accents: text.removeAccents,
  remove_special_chars: text.removeSpecialChars,
  
  // String operations
  split: string.split,
  split_comma: string.splitComma,
  join: string.join,
  replace: string.replace,
  replace_regex: string.replaceRegex,
  prefix: string.prefix,
  suffix: string.suffix,
  slugify: string.slugify,
  to_snake_case: string.toSnakeCase,
  to_camel_case: string.toCamelCase,
  to_pascal_case: string.toPascalCase,
  sanitize_filename: string.sanitizeFilename,
  
  // Numeric operations
  clean_numeric_value: numeric.cleanNumericValue,
  addition: numeric.addition,
  subtraction: numeric.subtraction,
  multiplication: numeric.multiplication,
  division: numeric.division,
  percentage: numeric.percentage,
  round_decimal: numeric.roundDecimal,
  absolute_value: numeric.absoluteValue,
  ceiling: numeric.ceiling,
  floor: numeric.floor,
  square_root: numeric.squareRoot,
  power: numeric.power,
  modulo: numeric.modulo,
  clamp: numeric.clamp,
  scale: numeric.scale,
  reciprocal: numeric.reciprocal,
  sign: numeric.sign,
  adjust_negative_to_zero: numeric.adjustNegativeToZero,
  zero_padding: numeric.zeroPadding,
  
  // Date operations
  date_only: date.dateOnly,
  format_date: date.formatDate,
  add_days: date.addDays,
  subtract_days: date.subtractDays,
  day_of_week: date.dayOfWeek,
  day_name: date.dayName,
  month_name: date.monthName,
  year: date.year,
  month: date.month,
  day: date.day,
  is_weekend: date.isWeekend,
  days_between: date.daysBetween,
  
  // List operations
  list_length: list.listLength,
  list_first: list.listFirst,
  list_last: list.listLast,
  list_unique: list.listUnique,
  list_sort: list.listSort,
  
  // Conditional operations
  if_empty: conditional.ifEmpty,
  if_null: conditional.ifNull,
  coalesce: conditional.coalesce,
  copy: conditional.copy,
  rejects: conditional.rejects,
  set: conditional.set,
  set_number: conditional.setNumber,
  
  // Utility operations
  clean_html: utility.cleanHtml,
  clean_upc: utility.cleanUpc,
  vlookup_map: utility.vlookupMap,
  url_encode: utility.urlEncode,
  url_decode: utility.urlDecode,
  base64_encode: utility.base64Encode,
  base64_decode: utility.base64Decode,
  md5_hash: utility.md5Hash,
  json_parse: utility.jsonParse,
  json_stringify: utility.jsonStringify,
  xml_escape: utility.xmlEscape,
  html_unescape: utility.htmlUnescape,
  currency_format: utility.currencyFormat,
  levenshtein_distance: utility.levenshteinDistance,
  string_similarity: utility.stringSimilarity,
  extract_domain: utility.extractDomain,
};

/**
 * Parse a DSL rule string into transformation steps
 * Example: "strip + uppercase + replace| |_"
 */
export function parseRuleString(ruleString: string): TransformationStep[] {
  const steps: TransformationStep[] = [];
  
  // Split by " + " to get individual operations
  const operations = ruleString.split(' + ');
  
  for (const op of operations) {
    const parts = op.split('|');
    const operation = parts[0].trim();
    const args = parts.slice(1);
    
    steps.push({
      operation,
      args: args.reduce((acc, arg, i) => {
        acc[`arg${i}`] = arg;
        return acc;
      }, {} as Record<string, any>),
    });
  }
  
  return steps;
}

/**
 * Apply a sequence of transformation steps to a value
 */
export function applyTransformations(value: any, steps: TransformationStep[]): any {
  let result = value;
  
  for (const step of steps) {
    const fn = TRANSFORMS[step.operation];
    
    if (!fn) {
      console.warn(`Unknown transformation: ${step.operation}`);
      continue;
    }
    
    try {
      // Extract arguments in order
      const args = Object.keys(step.args)
        .sort()
        .map((key) => step.args[key]);
      
      result = fn(result, ...args);
    } catch (error) {
      if (error instanceof RejectRow) {
        throw error; // Re-throw RejectRow errors
      }
      console.error(`Error in transformation ${step.operation}:`, error);
      // Continue with current value on error
    }
  }
  
  return result;
}

/**
 * Transform a single value using a rule string
 * Convenience function for simple use cases
 */
export function transform(value: any, ruleString: string): any {
  const steps = parseRuleString(ruleString);
  return applyTransformations(value, steps);
}

/**
 * Bulk apply transformations with broadcasting
 * Supports: single rule → many values, many rules → single value, n:n
 */
export function bulkApplyPipeRules(
  valuesList: any[],
  ruleStrings: string | string[]
): any[] {
  const rules = Array.isArray(ruleStrings) ? ruleStrings : [ruleStrings];
  
  // Broadcasting logic
  if (rules.length === 1) {
    // Single rule applied to all values
    const steps = parseRuleString(rules[0]);
    return valuesList.map((v) => {
      try {
        return applyTransformations(v, steps);
      } catch (error) {
        if (error instanceof RejectRow) {
          return null; // Mark rejected rows as null
        }
        return v;
      }
    });
  }
  
  if (valuesList.length === 1) {
    // Multiple rules applied to single value
    return rules.map((rule) => {
      try {
        const steps = parseRuleString(rule);
        return applyTransformations(valuesList[0], steps);
      } catch (error) {
        if (error instanceof RejectRow) {
          return null;
        }
        return valuesList[0];
      }
    });
  }
  
  if (valuesList.length === rules.length) {
    // One-to-one mapping
    return valuesList.map((v, i) => {
      try {
        const steps = parseRuleString(rules[i]);
        return applyTransformations(v, steps);
      } catch (error) {
        if (error instanceof RejectRow) {
          return null;
        }
        return v;
      }
    });
  }
  
  throw new Error(
    `Invalid broadcasting: ${valuesList.length} values and ${rules.length} rules. ` +
    'Must be 1:n, n:1, or n:n.'
  );
}

/**
 * Get all available transformation operations
 */
export function getAvailableTransforms(): string[] {
  return Object.keys(TRANSFORMS).sort();
}

/**
 * Check if a transformation exists
 */
export function hasTransform(name: string): boolean {
  return name in TRANSFORMS;
}
