/**
 * Transformation Tests
 * Test all transformation operations
 */

import { transform, bulkApplyPipeRules } from '../src/transformations';
import * as text from '../src/transformations/text';
import * as string from '../src/transformations/string';
import * as numeric from '../src/transformations/numeric';

describe('Text Transformations', () => {
  test('uppercase', () => {
    expect(text.uppercase('hello')).toBe('HELLO');
    expect(text.uppercase('Hello World')).toBe('HELLO WORLD');
  });

  test('lowercase', () => {
    expect(text.lowercase('HELLO')).toBe('hello');
    expect(text.lowercase('Hello World')).toBe('hello world');
  });

  test('strip', () => {
    expect(text.strip('  hello  ')).toBe('hello');
    expect(text.strip('\n\ttest\n')).toBe('test');
  });

  test('titleCase', () => {
    expect(text.titleCase('hello world')).toBe('Hello World');
    expect(text.titleCase('HELLO WORLD')).toBe('Hello World');
  });

  test('capitalize', () => {
    expect(text.capitalize('hello')).toBe('Hello');
    expect(text.capitalize('hello world')).toBe('Hello world');
  });
});

describe('String Transformations', () => {
  test('split', () => {
    expect(string.split('a,b,c', ',')).toEqual(['a', 'b', 'c']);
    expect(string.split('a b c', ' ')).toEqual(['a', 'b', 'c']);
  });

  test('join', () => {
    expect(string.join(['a', 'b', 'c'], ',')).toBe('a,b,c');
    expect(string.join(['a', 'b', 'c'], '-')).toBe('a-b-c');
  });

  test('replace', () => {
    expect(string.replace('hello world', 'world', 'there')).toBe('hello there');
    expect(string.replace('test test', 'test', 'demo')).toBe('demo demo');
  });

  test('slugify', () => {
    expect(string.slugify('Hello World')).toBe('hello-world');
    expect(string.slugify('Test  Multiple   Spaces')).toBe('test-multiple-spaces');
  });

  test('toSnakeCase', () => {
    expect(string.toSnakeCase('helloWorld')).toBe('hello_world');
    expect(string.toSnakeCase('Hello World')).toBe('hello_world');
  });
});

describe('Numeric Transformations', () => {
  test('cleanNumericValue', () => {
    expect(numeric.cleanNumericValue('$1,234.56')).toBe(1234.56);
    expect(numeric.cleanNumericValue('€999')).toBe(999);
  });

  test('addition', () => {
    expect(numeric.addition(10, 5)).toBe(15);
    expect(numeric.addition('20', 10)).toBe(30);
  });

  test('multiplication', () => {
    expect(numeric.multiplication(10, 2)).toBe(20);
    expect(numeric.multiplication('5', 3)).toBe(15);
  });

  test('roundDecimal', () => {
    expect(numeric.roundDecimal(3.14159, 2)).toBe(3.14);
    expect(numeric.roundDecimal(10.5, 0)).toBe(11);
  });

  test('clamp', () => {
    expect(numeric.clamp(5, 0, 10)).toBe(5);
    expect(numeric.clamp(-5, 0, 10)).toBe(0);
    expect(numeric.clamp(15, 0, 10)).toBe(10);
  });
});

describe('DSL Engine', () => {
  test('simple transformation', () => {
    expect(transform('hello', 'uppercase')).toBe('HELLO');
    expect(transform('  test  ', 'strip')).toBe('test');
  });

  test('chained transformations', () => {
    expect(transform('  hello  ', 'strip + uppercase')).toBe('HELLO');
    expect(transform('hello world', 'uppercase + replace| |_')).toBe('HELLO_WORLD');
  });

  test('transformations with parameters', () => {
    expect(transform('hello', 'prefix|SKU-')).toBe('SKU-hello');
    expect(transform('test', 'suffix|-001')).toBe('test-001');
  });

  test('complex transformation pipeline', () => {
    const result = transform(
      '  Hello World  ',
      'strip + lowercase + replace| |_ + uppercase'
    );
    expect(result).toBe('HELLO_WORLD');
  });
});

describe('Bulk Transformations', () => {
  test('single rule, multiple values', () => {
    const result = bulkApplyPipeRules(
      ['hello', 'world', 'test'],
      'uppercase'
    );
    expect(result).toEqual(['HELLO', 'WORLD', 'TEST']);
  });

  test('chained rules', () => {
    const result = bulkApplyPipeRules(
      ['  hello  ', '  world  '],
      'strip + uppercase'
    );
    expect(result).toEqual(['HELLO', 'WORLD']);
  });

  test('complex pipeline', () => {
    const result = bulkApplyPipeRules(
      ['Product 1', 'Product 2'],
      'lowercase + replace| |- + slugify'
    );
    expect(result).toEqual(['product-1', 'product-2']);
  });
});

describe('Edge Cases', () => {
  test('null and undefined handling', () => {
    expect(text.uppercase(null)).toBe(null);
    expect(text.strip(undefined)).toBe(undefined);
  });

  test('empty string handling', () => {
    expect(text.strip('')).toBe('');
    expect(text.uppercase('')).toBe('');
  });

  test('number inputs to text operations', () => {
    expect(text.uppercase(123)).toBe(123);
    expect(text.strip(456)).toBe(456);
  });
});
