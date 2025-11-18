/**
 * CSV/TSV Parser
 * Simple, efficient line-by-line parsing
 */

export interface CSVParserOptions {
  delimiter?: string;
  hasHeaders?: boolean;
  skipEmptyLines?: boolean;
}

export async function* parseCSV(
  content: string,
  options: CSVParserOptions = {}
): AsyncGenerator<Record<string, any>> {
  const {
    delimiter = ',',
    hasHeaders = true,
    skipEmptyLines = true,
  } = options;

  const lines = content.split('\n');
  let headers: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Skip empty lines
    if (skipEmptyLines && !line) continue;

    // Parse CSV line (simple implementation)
    const values = parseCSVLine(line, delimiter);

    // First line as headers
    if (i === 0 && hasHeaders) {
      headers = values;
      continue;
    }

    // Build row object
    const row: Record<string, any> = {};
    
    if (hasHeaders && headers.length > 0) {
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
    } else {
      values.forEach((value, index) => {
        row[`col_${index}`] = value;
      });
    }

    yield row;
  }
}

/**
 * Parse a single CSV line handling quotes
 */
function parseCSVLine(line: string, delimiter: string): string[] {
  const values: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    const next = line[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        // Escaped quote
        current += '"';
        i++; // Skip next quote
      } else {
        // Toggle quote state
        inQuotes = !inQuotes;
      }
    } else if (char === delimiter && !inQuotes) {
      // End of value
      values.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }

  // Add last value
  values.push(current.trim());

  return values;
}

export async function parseCSVFile(
  filePath: string,
  options: CSVParserOptions = {}
): Promise<Record<string, any>[]> {
  // For Node.js environment
  if (typeof require !== 'undefined') {
    const fs = require('fs');
    const content = fs.readFileSync(filePath, 'utf-8');
    const rows: Record<string, any>[] = [];
    
    for await (const row of parseCSV(content, options)) {
      rows.push(row);
    }
    
    return rows;
  }
  
  throw new Error('File reading not supported in browser environment');
}
