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

// NEW: Email validation
export const email: ValidatorFn = (value, _params) => {
  if (typeof value !== 'string') return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(value);
};

// NEW: URL validation
export const url: ValidatorFn = (value, _params) => {
  if (typeof value !== 'string') return false;
  try {
    new URL(value);
    return true;
  } catch {
    // Try with http:// prefix
    try {
      new URL(`http://${value}`);
      return value.includes('.');
    } catch {
      return false;
    }
  }
};

// NEW: Phone validation (supports multiple formats)
export const phone: ValidatorFn = (value, _params) => {
  if (typeof value !== 'string') return false;
  
  // Remove all non-digit characters
  const digits = value.replace(/\D/g, '');
  
  // Phone numbers are typically 10-15 digits
  if (digits.length < 10 || digits.length > 15) return false;
  
  // Common phone formats
  const phonePatterns = [
    /^\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}$/,  // US/Canada
    /^\+?\d{10,15}$/,  // International
    /^\d{10}$/,  // Simple 10-digit
  ];
  
  return phonePatterns.some(pattern => pattern.test(value));
};

// NEW: Credit card validation (Luhn algorithm)
export const creditCard: ValidatorFn = (value, _params) => {
  if (typeof value !== 'string') return false;
  
  // Remove all non-digit characters
  const digits = value.replace(/\D/g, '');
  
  // Must be 13-19 digits
  if (digits.length < 13 || digits.length > 19) return false;
  
  // Luhn algorithm
  let sum = 0;
  let double = false;
  
  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);
    
    if (double) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    
    sum += digit;
    double = !double;
  }
  
  return sum % 10 === 0;
};

// NEW: IP address validation (IPv4 and IPv6)
export const ipAddress: ValidatorFn = (value, _params) => {
  if (typeof value !== 'string') return false;
  
  // IPv4 validation
  const ipv4Regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  if (ipv4Regex.test(value)) return true;
  
  // IPv6 validation (simplified)
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  if (ipv6Regex.test(value)) return true;
  
  // IPv6 with :: compression
  const ipv6CompressedRegex = /^(([0-9a-fA-F]{1,4}:)*)?::([0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}$/;
  if (ipv6CompressedRegex.test(value)) return true;
  
  return false;
};
