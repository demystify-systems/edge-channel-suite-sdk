/**
 * Core transformation operations (28 operations)
 * Matches Python SDK operations.py for transformation parity
 */

import { RejectRow } from '../core/types';

/**
 * TEXT OPERATIONS
 */

export function uppercase(v: any): any {
  return typeof v === 'string' ? v.toUpperCase() : v;
}

export function lowercase(v: any): any {
  return typeof v === 'string' ? v.toLowerCase() : v;
}

export function strip(v: any): any {
  return typeof v === 'string' ? v.trim() : v;
}

export function title_case(v: any): any {
  if (typeof v !== 'string') return v;
  return v.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
}

export function capitalize(v: any): any {
  if (typeof v !== 'string' || v.length === 0) return v;
  return v.charAt(0).toUpperCase() + v.slice(1);
}

export function split(v: any, delimiter: string = ','): any {
  if (typeof v !== 'string') return v;
  
  // Handle special delimiter escaping
  if (delimiter === '|||' || delimiter === '\\|') {
    delimiter = '|';
  } else if (delimiter === '|| ' || delimiter === '||') {
    delimiter = ' ';
  }
  
  return v.split(delimiter);
}

export function split_comma(v: any): any {
  return split(v, ',');
}

export function join(v: any, delimiter: string = ','): any {
  if (Array.isArray(v)) {
    return v.join(delimiter);
  }
  return v;
}

export function replace(v: any, old_str: string, new_str: string): any {
  if (typeof v !== 'string') return v;
  return v.replace(new RegExp(old_str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), new_str);
}

export function replace_regex(v: any, pattern: string, replacement: string): any {
  if (typeof v !== 'string') return v;
  try {
    return v.replace(new RegExp(pattern, 'g'), replacement);
  } catch {
    return v;
  }
}

export function prefix(v: any, prefix_str: string): any {
  if (v === null || v === undefined || v === '') return v;
  return `${prefix_str}${v}`;
}

export function suffix(v: any, suffix_str: string): any {
  if (v === null || v === undefined || v === '') return v;
  return `${v}${suffix_str}`;
}

export function clean_html(v: any): any {
  if (typeof v !== 'string') return v;
  // Remove HTML tags
  let cleaned = v.replace(/<[^>]*>/g, '');
  // Decode HTML entities
  cleaned = cleaned
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
  return cleaned.trim();
}

export function clean_upc(v: any): any {
  if (typeof v !== 'string') return v;
  // Remove all non-digit characters
  let cleaned = v.replace(/\D/g, '');
  // Pad with zeros if needed (UPC should be 12 digits)
  if (cleaned.length > 0 && cleaned.length < 12) {
    cleaned = cleaned.padStart(12, '0');
  }
  return cleaned;
}

/**
 * NUMERIC OPERATIONS
 */

export function clean_numeric_value(v: any): any {
  if (typeof v === 'number') return v;
  if (typeof v !== 'string') return v;
  
  // Remove currency symbols, commas, spaces
  const cleaned = v.replace(/[$,\s]/g, '');
  const num = parseFloat(cleaned);
  return isNaN(num) ? v : num;
}

export function addition(v: any, amount: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num + amount;
}

export function subtraction(v: any, amount: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num - amount;
}

export function multiplication(v: any, factor: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num * factor;
}

export function division(v: any, divisor: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num) || divisor === 0) return v;
  return num / divisor;
}

export function percentage(v: any, percent: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : (num * percent) / 100;
}

export function adjust_negative_to_zero(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return num < 0 ? 0 : num;
}

export function zero_padding(v: any, length: number): any {
  const str = String(v);
  return str.padStart(length, '0');
}

/**
 * DATE OPERATIONS
 */

export function date_only(v: any): any {
  if (v instanceof Date) {
    return v.toISOString().split('T')[0];
  }
  if (typeof v === 'string') {
    try {
      const date = new Date(v);
      return date.toISOString().split('T')[0];
    } catch {
      return v;
    }
  }
  return v;
}

/**
 * CONTROL OPERATIONS
 */

export function copy(v: any): any {
  return v;
}

export function rejects(_v: any, message?: string): never {
  throw new RejectRow(message || 'Row rejected');
}

export function set(_v: any, value: string): any {
  return value;
}

export function set_number(_v: any, value: number): any {
  return value;
}

/**
 * LOOKUP OPERATIONS
 */

export function vlookup_map(v: any, mappings: string): any {
  if (v === null || v === undefined) return v;
  
  // Parse mappings: "key1:value1,key2:value2"
  const mapping: Record<string, string> = {};
  const pairs = mappings.split(',');
  
  for (const pair of pairs) {
    const [key, value] = pair.split(':');
    if (key && value) {
      mapping[key.trim()] = value.trim();
    }
  }
  
  const key = String(v);
  return mapping[key] || v;
}
