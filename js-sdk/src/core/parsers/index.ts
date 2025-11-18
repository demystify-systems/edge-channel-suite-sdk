/**
 * File parsers - modular exports
 */

export * from './csv';
export * from './json';
export * from './xml';

// Convenience function to detect and parse based on file extension
export async function parseFile(
  filePath: string,
  format?: 'csv' | 'tsv' | 'json' | 'xml'
): Promise<Record<string, any>[]> {
  const detectedFormat = format || detectFormat(filePath);
  
  switch (detectedFormat) {
    case 'csv':
      const { parseCSVFile } = await import('./csv');
      return parseCSVFile(filePath, { delimiter: ',' });
    
    case 'tsv':
      const { parseCSVFile: parseTSVFile } = await import('./csv');
      return parseTSVFile(filePath, { delimiter: '\t' });
    
    case 'json':
      const { parseJSONFile } = await import('./json');
      return parseJSONFile(filePath);
    
    case 'xml':
      const { parseXMLFile } = await import('./xml');
      return parseXMLFile(filePath);
    
    default:
      throw new Error(`Unsupported file format: ${detectedFormat}`);
  }
}

function detectFormat(filePath: string): string {
  const ext = filePath.split('.').pop()?.toLowerCase();
  return ext || 'csv';
}
