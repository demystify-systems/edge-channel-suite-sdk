/**
 * Validation rules
 * Small, testable, easy to debug
 */

import { ValidatorFn } from '../core/types';

export const required: ValidatorFn = (value, _params) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string' && value.trim() === '') return false;
  if (Array.isArray(value) && value.length === 0) return false;
  return true;
};

export const maxLength: ValidatorFn = (value, params) => {
  if (typeof value !== 'string') return true;
  const max = params.max || params.max_length;
  return value.length <= max;
};

export const minLength: ValidatorFn = (value, params) => {
  if (typeof value !== 'string') return true;
  const min = params.min || params.min_length;
  return value.length >= min;
};

export const regex: ValidatorFn = (value, params) => {
  if (typeof value !== 'string') return true;
  try {
    const pattern = new RegExp(params.pattern);
    return pattern.test(value);
  } catch {
    return false;
  }
};

export const enumValidator: ValidatorFn = (value, params) => {
  const allowed = params.values || params.enum || [];
  return allowed.includes(value);
};

export const numericRange: ValidatorFn = (value, params) => {
  const num = typeof value === 'number' ? value : parseFloat(value);
  if (isNaN(num)) return false;
  
  const min = params.min !== undefined ? params.min : -Infinity;
  const max = params.max !== undefined ? params.max : Infinity;
  
  return num >= min && num <= max;
};

export const dateBefore: ValidatorFn = (value, params) => {
  try {
    const date = new Date(value);
    const before = new Date(params.date || params.before);
    return date < before;
  } catch {
    return false;
  }
};

export const dateAfter: ValidatorFn = (value, params) => {
  try {
    const date = new Date(value);
    const after = new Date(params.date || params.after);
    return date > after;
  } catch {
    return false;
  }
};

export const customExpression: ValidatorFn = (value, params) => {
  // Simple expression evaluator
  // For now, just return true - full implementation would need safe eval
  console.warn('custom_expression validation not fully implemented');
  return true;
};
