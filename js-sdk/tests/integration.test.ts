/**
 * Integration Tests
 * End-to-end workflow tests
 */

import { transformData, validateData } from '../src/pipelines/orchestrator';
import { buildCSV, buildJSON } from '../src/export/builders';
import { parseCSV } from '../src/core/parsers/csv';

describe('Integration: Transform and Validate Pipeline', () => {
  test('transform product data', () => {
    const products = [
      { sku: '  abc123  ', title: 'PRODUCT ONE', price: '$99.99' },
      { sku: '  xyz789  ', title: 'PRODUCT TWO', price: '$149.50' },
    ];

    const transformed = transformData(products, {
      transformations: {
        sku: 'strip + uppercase',
        title: 'title_case',
        price: 'clean_numeric_value + round_decimal|2',
      },
    });

    expect(transformed[0].sku).toBe('ABC123');
    expect(transformed[0].title).toBe('Product One');
    expect(transformed[0].price).toBe(99.99);
  });

  test('validate and filter data', () => {
    const products = [
      { sku: 'ABC123', title: 'Product One', price: 99.99 },
      { sku: '', title: 'X', price: -10 },
      { sku: 'XYZ789', title: 'Product Two', price: 149.50 },
    ];

    const { valid, invalid, errors } = validateData(products, {
      sku: [{ rule_type: 'required', field_name: 'sku', params: {} }],
      title: [{ rule_type: 'min_length', field_name: 'title', params: { min: 3 } }],
      price: [{ rule_type: 'numeric_range', field_name: 'price', params: { min: 0 } }],
    });

    expect(valid.length).toBe(2);
    expect(invalid.length).toBe(1);
    expect(Object.keys(errors).length).toBe(1);
  });

  test('complete workflow: parse, transform, validate, export', async () => {
    // Sample CSV data
    const csvData = `sku,title,price
"  abc123  ","PRODUCT ONE","$99.99"
"  xyz789  ","PRODUCT TWO","$149.50"`;

    // Parse CSV
    const rows: Record<string, any>[] = [];
    for await (const row of parseCSV(csvData)) {
      rows.push(row);
    }

    // Transform
    const transformed = transformData(rows, {
      transformations: {
        sku: 'strip + uppercase',
        title: 'title_case',
        price: 'clean_numeric_value + round_decimal|2',
      },
    });

    // Validate
    const { valid } = validateData(transformed, {
      sku: [{ rule_type: 'required', field_name: 'sku', params: {} }],
      price: [{ rule_type: 'numeric_range', field_name: 'price', params: { min: 0 } }],
    });

    // Export to JSON
    const json = buildJSON(valid, { pretty: true });
    expect(json).toContain('ABC123');
    expect(json).toContain('Product One');

    // Export to CSV
    const csv = buildCSV(valid);
    expect(csv).toContain('ABC123');
    expect(csv.split('\n').length).toBe(3); // Header + 2 rows
  });
});

describe('Integration: File Builders', () => {
  test('CSV builder', () => {
    const data = [
      { sku: 'ABC123', title: 'Product One', price: 99.99 },
      { sku: 'XYZ789', title: 'Product Two', price: 149.50 },
    ];

    const csv = buildCSV(data);
    const lines = csv.split('\n');

    expect(lines[0]).toBe('sku,title,price');
    expect(lines[1]).toContain('ABC123');
    expect(lines[2]).toContain('XYZ789');
  });

  test('JSON builder', () => {
    const data = [
      { sku: 'ABC123', title: 'Product One', price: 99.99 },
    ];

    const json = buildJSON(data);
    const parsed = JSON.parse(json);

    expect(parsed.length).toBe(1);
    expect(parsed[0].sku).toBe('ABC123');
  });
});

describe('Integration: CSV Parser', () => {
  test('parse simple CSV', async () => {
    const csv = `name,age,city
Alice,30,NYC
Bob,25,LA`;

    const rows: Record<string, any>[] = [];
    for await (const row of parseCSV(csv)) {
      rows.push(row);
    }

    expect(rows.length).toBe(2);
    expect(rows[0].name).toBe('Alice');
    expect(rows[1].city).toBe('LA');
  });

  test('parse CSV with quotes', async () => {
    const csv = `name,description
"Product One","High quality, tested"
"Product Two","Easy to use"`;

    const rows: Record<string, any>[] = [];
    for await (const row of parseCSV(csv)) {
      rows.push(row);
    }

    expect(rows.length).toBe(2);
    expect(rows[0].description).toContain('tested');
  });
});
