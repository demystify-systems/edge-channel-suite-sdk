/**
 * Utility and cleaning operations
 */

export function cleanHtml(v: any): any {
  if (typeof v !== 'string') return v;
  
  // Remove HTML tags
  let cleaned = v.replace(/<[^>]*>/g, '');
  
  // Decode HTML entities
  cleaned = cleaned
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'");
  
  return cleaned.trim();
}

export function cleanUpc(v: any): any {
  if (typeof v !== 'string') return v;
  
  // Remove all non-digit characters
  let cleaned = v.replace(/\D/g, '');
  
  // Pad with zeros if needed (UPC should be 12 digits)
  if (cleaned.length > 0 && cleaned.length < 12) {
    cleaned = cleaned.padStart(12, '0');
  }
  
  return cleaned;
}

export function vlookupMap(v: any, mappings: string): any {
  if (v === null || v === undefined) return v;
  
  // Parse mappings: "key1:value1,key2:value2"
  const mapping: Record<string, string> = {};
  const pairs = mappings.split(',');
  
  for (const pair of pairs) {
    const [key, value] = pair.split(':');
    if (key && value) {
      mapping[key.trim()] = value.trim();
    }
  }
  
  const key = String(v);
  return mapping[key] || v;
}
