/**
 * JSON Parser
 * Parse JSON arrays or line-delimited JSON (NDJSON)
 */

export interface JSONParserOptions {
  format?: 'array' | 'ndjson';
}

export async function* parseJSON(
  content: string,
  options: JSONParserOptions = {}
): AsyncGenerator<Record<string, any>> {
  const { format = 'array' } = options;

  if (format === 'ndjson') {
    // Line-delimited JSON
    const lines = content.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      
      try {
        yield JSON.parse(trimmed);
      } catch (error) {
        console.error('Error parsing JSON line:', error);
      }
    }
  } else {
    // Standard JSON array
    try {
      const data = JSON.parse(content);
      
      if (Array.isArray(data)) {
        for (const item of data) {
          yield item;
        }
      } else {
        // Single object
        yield data;
      }
    } catch (error) {
      console.error('Error parsing JSON:', error);
      throw error;
    }
  }
}

export async function parseJSONFile(
  filePath: string,
  options: JSONParserOptions = {}
): Promise<Record<string, any>[]> {
  if (typeof require !== 'undefined') {
    const fs = require('fs');
    const content = fs.readFileSync(filePath, 'utf-8');
    const rows: Record<string, any>[] = [];
    
    for await (const row of parseJSON(content, options)) {
      rows.push(row);
    }
    
    return rows;
  }
  
  throw new Error('File reading not supported in browser environment');
}
