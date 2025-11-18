/**
 * Conditional and control flow operations
 */

import { RejectRow } from '../core/types';

export function ifEmpty(v: any, defaultValue: any): any {
  if (v === null || v === undefined || v === '' || (Array.isArray(v) && v.length === 0)) {
    return defaultValue;
  }
  return v;
}

export function ifNull(v: any, defaultValue: any): any {
  return v === null || v === undefined ? defaultValue : v;
}

export function coalesce(v: any, ...fallbacks: any[]): any {
  if (v !== null && v !== undefined && v !== '') {
    return v;
  }
  
  for (const fallback of fallbacks) {
    if (fallback !== null && fallback !== undefined && fallback !== '') {
      return fallback;
    }
  }
  
  return v;
}

export function copy(v: any): any {
  return v;
}

export function rejects(_v: any, message?: string): never {
  throw new RejectRow(message || 'Row rejected');
}

export function set(_v: any, value: any): any {
  return value;
}

export function setNumber(_v: any, value: number): any {
  return value;
}
