/**
 * XML Parser
 * Simple XML to JSON conversion
 */

export interface XMLParserOptions {
  rootElement?: string;
  itemElement?: string;
}

export async function* parseXML(
  content: string,
  options: XMLParserOptions = {}
): AsyncGenerator<Record<string, any>> {
  const { itemElement = 'item' } = options;

  // Simple regex-based XML parsing
  const itemRegex = new RegExp(`<${itemElement}[^>]*>(.*?)</${itemElement}>`, 'gs');
  const matches = content.matchAll(itemRegex);

  for (const match of matches) {
    const itemContent = match[1];
    const obj = xmlToObject(itemContent);
    yield obj;
  }
}

/**
 * Convert XML string to JavaScript object
 * Simple implementation for basic XML structures
 */
function xmlToObject(xml: string): Record<string, any> {
  const obj: Record<string, any> = {};
  
  // Match all tags
  const tagRegex = /<(\w+)[^>]*>(.*?)<\/\1>/gs;
  const matches = xml.matchAll(tagRegex);

  for (const match of matches) {
    const tagName = match[1];
    const tagValue = match[2].trim();
    
    // Check if value contains nested tags
    if (tagValue.includes('<')) {
      obj[tagName] = xmlToObject(tagValue);
    } else {
      obj[tagName] = tagValue;
    }
  }

  return obj;
}

export async function parseXMLFile(
  filePath: string,
  options: XMLParserOptions = {}
): Promise<Record<string, any>[]> {
  if (typeof require !== 'undefined') {
    const fs = require('fs');
    const content = fs.readFileSync(filePath, 'utf-8');
    const rows: Record<string, any>[] = [];
    
    for await (const row of parseXML(content, options)) {
      rows.push(row);
    }
    
    return rows;
  }
  
  throw new Error('File reading not supported in browser environment');
}
