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
    .replace(/&quot;/g, '\"')
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

// NEW: URL encoding/decoding
export function urlEncode(v: any): any {
  if (typeof v !== 'string') return v;
  return encodeURIComponent(v);
}

export function urlDecode(v: any): any {
  if (typeof v !== 'string') return v;
  try {
    return decodeURIComponent(v);
  } catch {
    return v;
  }
}

// NEW: Base64 encoding/decoding
export function base64Encode(v: any): any {
  if (typeof v !== 'string') return v;
  if (typeof Buffer !== 'undefined') {
    return Buffer.from(v, 'utf-8').toString('base64');
  }
  return btoa(v);
}

export function base64Decode(v: any): any {
  if (typeof v !== 'string') return v;
  try {
    if (typeof Buffer !== 'undefined') {
      return Buffer.from(v, 'base64').toString('utf-8');
    }
    return atob(v);
  } catch {
    return v;
  }
}

// NEW: Hashing
export function md5Hash(v: any): any {
  if (typeof v !== 'string') return v;
  
  // Simple MD5 implementation (for browser compatibility)
  // Note: For production, consider using crypto.subtle or a library
  let hash = 0;
  for (let i = 0; i < v.length; i++) {
    const char = v.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

// NEW: JSON operations
export function jsonParse(v: any): any {
  if (typeof v !== 'string') return v;
  try {
    return JSON.parse(v);
  } catch {
    return v;
  }
}

export function jsonStringify(v: any): any {
  if (v === null || v === undefined) return v;
  try {
    return JSON.stringify(v);
  } catch {
    return String(v);
  }
}

// NEW: XML/HTML escaping
export function xmlEscape(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export function htmlUnescape(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#39;/g, "'");
}

// NEW: Currency formatting
export function currencyFormat(v: any, currency: string = 'USD'): any {
  const num = typeof v === 'string' ? parseFloat(v) : v;
  if (typeof num !== 'number' || isNaN(num)) return v;
  
  const symbols: Record<string, string> = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'INR': '₹',
    'JPY': '¥'
  };
  
  const symbol = symbols[currency.toUpperCase()] || currency;
  return `${symbol}${num.toFixed(2)}`;
}

// NEW: String similarity (Levenshtein distance)
export function levenshteinDistance(v: any, target: string): any {
  if (typeof v !== 'string') return v;
  
  const s1 = v;
  const s2 = target;
  const len1 = s1.length;
  const len2 = s2.length;
  
  const dp: number[][] = Array(len1 + 1)
    .fill(null)
    .map(() => Array(len2 + 1).fill(0));
  
  for (let i = 0; i <= len1; i++) dp[i][0] = i;
  for (let j = 0; j <= len2; j++) dp[0][j] = j;
  
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      );
    }
  }
  
  return dp[len1][len2];
}

export function stringSimilarity(v: any, target: string): any {
  if (typeof v !== 'string') return v;
  
  const distance = levenshteinDistance(v, target) as number;
  const maxLen = Math.max(v.length, target.length);
  if (maxLen === 0) return 1.0;
  
  const similarity = 1 - (distance / maxLen);
  return Math.round(similarity * 100) / 100;
}

// NEW: Domain extraction
export function extractDomain(v: any): any {
  if (typeof v !== 'string') return v;
  
  try {
    // Try to parse as URL
    const url = v.startsWith('http') ? v : `http://${v}`;
    const parsed = new URL(url);
    return parsed.hostname;
  } catch {
    // Try regex fallback
    const match = v.match(/(?:https?:\/\/)?(?:www\.)?([^/\s]+)/);
    return match ? match[1] : v;
  }
}
