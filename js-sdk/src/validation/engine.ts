/**
 * Validation Engine
 * Executes validation rules and collects errors
 */

import { ValidationRule, ValidationError, ValidatorFn } from '../core/types';
import * as rules from './rules';

// Registry of validation functions
const VALIDATORS: Record<string, ValidatorFn> = {
  required: rules.required,
  max_length: rules.maxLength,
  min_length: rules.minLength,
  regex: rules.regex,
  enum: rules.enumValidator,
  numeric_range: rules.numericRange,
  date_before: rules.dateBefore,
  date_after: rules.dateAfter,
  custom_expression: rules.customExpression,
  email: rules.email,
  url: rules.url,
  phone: rules.phone,
  credit_card: rules.creditCard,
  ip_address: rules.ipAddress,
};

/**
 * Validate a single value against multiple rules
 */
export function validate(value: any, validationRules: ValidationRule[]): ValidationError[] {
  const errors: ValidationError[] = [];
  
  for (const rule of validationRules) {
    const validator = VALIDATORS[rule.rule_type];
    
    if (!validator) {
      console.warn(`Unknown validation rule: ${rule.rule_type}`);
      continue;
    }
    
    try {
      const isValid = validator(value, rule.params);
      
      if (!isValid) {
        errors.push({
          field: rule.field_name,
          message: rule.error_message || `Validation failed: ${rule.rule_type}`,
          rule_type: rule.rule_type,
          value,
        });
      }
    } catch (error) {
      console.error(`Error in validation ${rule.rule_type}:`, error);
      errors.push({
        field: rule.field_name,
        message: `Validation error: ${error}`,
        rule_type: rule.rule_type,
        value,
      });
    }
  }
  
  return errors;
}

/**
 * Validate an entire row/object against attribute rules
 */
export function validateRow(
  row: Record<string, any>,
  attributeRules: Record<string, ValidationRule[]>
): Record<string, ValidationError[]> {
  const allErrors: Record<string, ValidationError[]> = {};
  
  for (const [field, rules] of Object.entries(attributeRules)) {
    const value = row[field];
    const errors = validate(value, rules);
    
    if (errors.length > 0) {
      allErrors[field] = errors;
    }
  }
  
  return allErrors;
}

/**
 * Get all available validators
 */
export function getAvailableValidators(): string[] {
  return Object.keys(VALIDATORS).sort();
}

/**
 * Check if a validator exists
 */
export function hasValidator(name: string): boolean {
  return name in VALIDATORS;
}
