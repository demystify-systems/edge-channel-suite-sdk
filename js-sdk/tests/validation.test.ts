/**
 * Validation Tests
 */

import { validate, validateRow } from '../src/validation';
import * as rules from '../src/validation/rules';

describe('Validation Rules', () => {
  test('required', () => {
    expect(rules.required('test', {})).toBe(true);
    expect(rules.required('', {})).toBe(false);
    expect(rules.required(null, {})).toBe(false);
    expect(rules.required(undefined, {})).toBe(false);
  });

  test('maxLength', () => {
    expect(rules.maxLength('test', { max: 10 })).toBe(true);
    expect(rules.maxLength('test', { max: 3 })).toBe(false);
    expect(rules.maxLength('hello', { max_length: 5 })).toBe(true);
  });

  test('minLength', () => {
    expect(rules.minLength('test', { min: 3 })).toBe(true);
    expect(rules.minLength('ab', { min: 3 })).toBe(false);
  });

  test('regex', () => {
    expect(rules.regex('test@example.com', { pattern: '^[\\w]+@[\\w]+\\.[\\w]+$' })).toBe(true);
    expect(rules.regex('invalid-email', { pattern: '^[\\w]+@[\\w]+\\.[\\w]+$' })).toBe(false);
  });

  test('enumValidator', () => {
    expect(rules.enumValidator('red', { values: ['red', 'blue', 'green'] })).toBe(true);
    expect(rules.enumValidator('yellow', { values: ['red', 'blue', 'green'] })).toBe(false);
  });

  test('numericRange', () => {
    expect(rules.numericRange(5, { min: 0, max: 10 })).toBe(true);
    expect(rules.numericRange(-1, { min: 0, max: 10 })).toBe(false);
    expect(rules.numericRange(15, { min: 0, max: 10 })).toBe(false);
  });
});

describe('Validation Engine', () => {
  test('single validation rule', () => {
    const errors = validate('test', [
      { rule_type: 'required', field_name: 'title', params: {} }
    ]);
    expect(errors.length).toBe(0);
  });

  test('failed validation', () => {
    const errors = validate('', [
      { rule_type: 'required', field_name: 'title', params: {} }
    ]);
    expect(errors.length).toBe(1);
    expect(errors[0].field).toBe('title');
    expect(errors[0].rule_type).toBe('required');
  });

  test('multiple validation rules', () => {
    const errors = validate('ab', [
      { rule_type: 'required', field_name: 'sku', params: {} },
      { rule_type: 'min_length', field_name: 'sku', params: { min: 3 } }
    ]);
    expect(errors.length).toBe(1);
    expect(errors[0].rule_type).toBe('min_length');
  });

  test('all validations pass', () => {
    const errors = validate('test@example.com', [
      { rule_type: 'required', field_name: 'email', params: {} },
      { rule_type: 'regex', field_name: 'email', params: { pattern: '^[\\w\\.-]+@[\\w\\.-]+\\.[\\w]+$' } }
    ]);
    expect(errors.length).toBe(0);
  });
});

describe('Row Validation', () => {
  test('validate entire row', () => {
    const row = {
      sku: 'ABC123',
      title: 'Product Name',
      price: 99.99
    };

    const validationRules = {
      sku: [
        { rule_type: 'required', field_name: 'sku', params: {} },
        { rule_type: 'min_length', field_name: 'sku', params: { min: 3 } }
      ],
      title: [
        { rule_type: 'required', field_name: 'title', params: {} },
        { rule_type: 'max_length', field_name: 'title', params: { max: 200 } }
      ],
      price: [
        { rule_type: 'required', field_name: 'price', params: {} },
        { rule_type: 'numeric_range', field_name: 'price', params: { min: 0 } }
      ]
    };

    const errors = validateRow(row, validationRules);
    expect(Object.keys(errors).length).toBe(0);
  });

  test('row with validation errors', () => {
    const row = {
      sku: '',
      title: 'P',
      price: -10
    };

    const validationRules = {
      sku: [
        { rule_type: 'required', field_name: 'sku', params: {} }
      ],
      title: [
        { rule_type: 'min_length', field_name: 'title', params: { min: 3 } }
      ],
      price: [
        { rule_type: 'numeric_range', field_name: 'price', params: { min: 0 } }
      ]
    };

    const errors = validateRow(row, validationRules);
    expect(Object.keys(errors).length).toBe(3);
    expect(errors.sku).toBeDefined();
    expect(errors.title).toBeDefined();
    expect(errors.price).toBeDefined();
  });
});
