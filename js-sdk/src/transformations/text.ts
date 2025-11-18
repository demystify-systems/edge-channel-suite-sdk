/**
 * Text transformation operations
 * Small, focused, easy to test and debug
 */

export function uppercase(v: any): any {
  return typeof v === 'string' ? v.toUpperCase() : v;
}

export function lowercase(v: any): any {
  return typeof v === 'string' ? v.toLowerCase() : v;
}

export function strip(v: any): any {
  return typeof v === 'string' ? v.trim() : v;
}

export function titleCase(v: any): any {
  if (typeof v !== 'string') return v;
  return v.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
}

export function capitalize(v: any): any {
  if (typeof v !== 'string' || v.length === 0) return v;
  return v.charAt(0).toUpperCase() + v.slice(1);
}

export function removeWhitespace(v: any): any {
  return typeof v === 'string' ? v.replace(/\s+/g, '') : v;
}

export function truncate(v: any, maxLength: number): any {
  if (typeof v !== 'string') return v;
  return v.length > maxLength ? v.substring(0, maxLength) : v;
}

export function padLeft(v: any, length: number, char: string = ' '): any {
  const str = String(v);
  return str.padStart(length, char);
}

export function padRight(v: any, length: number, char: string = ' '): any {
  const str = String(v);
  return str.padEnd(length, char);
}

export function reverseString(v: any): any {
  return typeof v === 'string' ? v.split('').reverse().join('') : v;
}

export function wordCount(v: any): any {
  if (typeof v !== 'string') return v;
  return v.trim().split(/\s+/).filter(Boolean).length;
}

export function charCount(v: any): any {
  return typeof v === 'string' ? v.length : v;
}

export function extractNumbers(v: any): any {
  if (typeof v !== 'string') return v;
  const numbers = v.match(/\d+/g);
  return numbers ? numbers.join('') : '';
}

export function extractLetters(v: any): any {
  if (typeof v !== 'string') return v;
  return v.replace(/[^a-zA-Z]/g, '');
}

export function removeAccents(v: any): any {
  if (typeof v !== 'string') return v;
  return v.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

export function removeSpecialChars(v: any): any {
  if (typeof v !== 'string') return v;
  return v.replace(/[^a-zA-Z0-9\s]/g, '');
}
