/**
 * File builders for export
 * Generate CSV, TSV, JSON, XML from data
 */

export interface FileBuilderOptions {
  format: 'csv' | 'tsv' | 'json' | 'xml' | 'xlsx';
  headers?: string[];
  pretty?: boolean;
  rootElement?: string;
  itemElement?: string;
  sheetName?: string;
}

export function buildCSV(
  data: Record<string, any>[],
  options: { delimiter?: string; headers?: string[] } = {}
): string {
  const { delimiter = ',', headers } = options;
  
  if (data.length === 0) return '';
  
  // Get headers from first row or use provided
  const cols = headers || Object.keys(data[0]);
  
  // Build CSV
  const lines: string[] = [];
  
  // Add header row
  lines.push(cols.map(escapeCSVValue).join(delimiter));
  
  // Add data rows
  for (const row of data) {
    const values = cols.map(col => escapeCSVValue(row[col]));
    lines.push(values.join(delimiter));
  }
  
  return lines.join('\n');
}

export function buildTSV(
  data: Record<string, any>[],
  options: { headers?: string[] } = {}
): string {
  return buildCSV(data, { ...options, delimiter: '\t' });
}

export function buildJSON(
  data: Record<string, any>[],
  options: { pretty?: boolean } = {}
): string {
  const { pretty = false } = options;
  return JSON.stringify(data, null, pretty ? 2 : 0);
}

export function buildXML(
  data: Record<string, any>[],
  options: { rootElement?: string; itemElement?: string; pretty?: boolean } = {}
): string {
  const {
    rootElement = 'root',
    itemElement = 'item',
    pretty = false,
  } = options;
  
  const indent = pretty ? 2 : 0;
  const nl = pretty ? '\n' : '';
  const space = (level: number) => pretty ? ' '.repeat(level * indent) : '';
  
  let xml = `<?xml version="1.0" encoding="UTF-8"?>${nl}`;
  xml += `<${rootElement}>${nl}`;
  
  for (const item of data) {
    xml += `${space(1)}<${itemElement}>${nl}`;
    xml += objectToXML(item, 2, indent, nl);
    xml += `${space(1)}</${itemElement}>${nl}`;
  }
  
  xml += `</${rootElement}>`;
  
  return xml;
}

function objectToXML(
  obj: Record<string, any>,
  level: number,
  indent: number,
  nl: string
): string {
  let xml = '';
  const space = ' '.repeat(level * indent);
  
  for (const [key, value] of Object.entries(obj)) {
    if (value === null || value === undefined) continue;
    
    if (typeof value === 'object' && !Array.isArray(value)) {
      xml += `${space}<${key}>${nl}`;
      xml += objectToXML(value, level + 1, indent, nl);
      xml += `${space}</${key}>${nl}`;
    } else if (Array.isArray(value)) {
      for (const item of value) {
        xml += `${space}<${key}>${escapeXML(String(item))}</${key}>${nl}`;
      }
    } else {
      xml += `${space}<${key}>${escapeXML(String(value))}</${key}>${nl}`;
    }
  }
  
  return xml;
}

function escapeCSVValue(value: any): string {
  if (value === null || value === undefined) return '';
  
  const str = String(value);
  
  // If contains comma, quote, or newline, wrap in quotes
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  
  return str;
}

function escapeXML(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Build XLSX file
 * Note: Requires xlsx library (npm install xlsx)
 */
export async function buildXLSX(
  data: Record<string, any>[],
  options: { headers?: string[]; sheetName?: string } = {}
): Promise<Buffer> {
  // Dynamic import to avoid bundling if not used
  let XLSX: any;
  try {
    XLSX = await import('xlsx');
  } catch (error) {
    throw new Error(
      'xlsx library not installed. Install with: npm install xlsx'
    );
  }

  const { headers, sheetName = 'Sheet1' } = options;
  
  if (data.length === 0) {
    return Buffer.from('');
  }
  
  // Get headers from first row or use provided
  const cols = headers || Object.keys(data[0]);
  
  // Convert data to array of arrays
  const rows = [cols]; // Header row
  for (const row of data) {
    rows.push(cols.map(col => row[col] !== undefined ? row[col] : ''));
  }
  
  // Create workbook and worksheet
  const worksheet = XLSX.utils.aoa_to_sheet(rows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  
  // Write to buffer
  const buffer = XLSX.write(workbook, {
    type: 'buffer',
    bookType: 'xlsx',
  });
  
  return buffer;
}

export function buildFile(
  data: Record<string, any>[],
  options: FileBuilderOptions
): string | Promise<Buffer> {
  switch (options.format) {
    case 'csv':
      return buildCSV(data, options);
    case 'tsv':
      return buildTSV(data, options);
    case 'json':
      return buildJSON(data, options);
    case 'xml':
      return buildXML(data, options);
    case 'xlsx':
      return buildXLSX(data, options);
    default:
      throw new Error(`Unsupported format: ${options.format}`);
  }
}

export async function writeFile(
  filePath: string,
  content: string
): Promise<void> {
  if (typeof require !== 'undefined') {
    const fs = require('fs');
    fs.writeFileSync(filePath, content, 'utf-8');
  } else {
    throw new Error('File writing not supported in browser environment');
  }
}
