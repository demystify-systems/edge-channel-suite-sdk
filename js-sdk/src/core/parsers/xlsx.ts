/**
 * XLSX Parser
 * Parses Excel files (.xlsx, .xlsm)
 * 
 * Note: Requires xlsx library (https://www.npmjs.com/package/xlsx)
 * Install with: npm install xlsx
 */

import { FileParser, ParsedRow } from '../types';

export class XLSXParser implements FileParser {
  private sheetName?: string;

  constructor(options?: { sheetName?: string }) {
    this.sheetName = options?.sheetName;
  }

  async *parse(filePath: string): AsyncGenerator<ParsedRow> {
    // Dynamic import to avoid bundling if not used
    let XLSX: any;
    try {
      XLSX = await import('xlsx');
    } catch (error) {
      throw new Error(
        'xlsx library not installed. Install with: npm install xlsx'
      );
    }

    // Read workbook
    const workbook = XLSX.readFile(filePath, {
      type: 'file',
      cellDates: true,
      dateNF: 'yyyy-mm-dd',
    });

    // Get sheet name
    const sheetName = this.sheetName || workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];

    if (!sheet) {
      throw new Error(`Sheet "${sheetName}" not found in workbook`);
    }

    // Convert sheet to JSON
    const rows: any[] = XLSX.utils.sheet_to_json(sheet, {
      header: 1,
      defval: null,
      raw: false,
    });

    if (rows.length === 0) {
      return;
    }

    // First row is headers
    const headers = rows[0];
    
    // Yield data rows
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const data: Record<string, any> = {};

      // Map array values to header keys
      headers.forEach((header: string, index: number) => {
        if (header) {
          data[header] = row[index] !== undefined ? row[index] : null;
        }
      });

      yield {
        file_row_number: i + 1, // 1-indexed (row 1 is headers)
        data,
      };
    }
  }

  /**
   * Parse from buffer (useful for uploaded files)
   */
  async *parseBuffer(buffer: Buffer): AsyncGenerator<ParsedRow> {
    let XLSX: any;
    try {
      XLSX = await import('xlsx');
    } catch (error) {
      throw new Error(
        'xlsx library not installed. Install with: npm install xlsx'
      );
    }

    const workbook = XLSX.read(buffer, {
      type: 'buffer',
      cellDates: true,
      dateNF: 'yyyy-mm-dd',
    });

    const sheetName = this.sheetName || workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];

    if (!sheet) {
      throw new Error(`Sheet "${sheetName}" not found in workbook`);
    }

    const rows: any[] = XLSX.utils.sheet_to_json(sheet, {
      header: 1,
      defval: null,
      raw: false,
    });

    if (rows.length === 0) {
      return;
    }

    const headers = rows[0];
    
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const data: Record<string, any> = {};

      headers.forEach((header: string, index: number) => {
        if (header) {
          data[header] = row[index] !== undefined ? row[index] : null;
        }
      });

      yield {
        file_row_number: i + 1,
        data,
      };
    }
  }
}
