/**
 * String manipulation operations (split, join, replace, etc.)
 */

export function split(v: any, delimiter: string = ','): any {
  if (typeof v !== 'string') return v;
  
  // Handle special delimiter escaping
  if (delimiter === '|||' || delimiter === '\\|') {
    delimiter = '|';
  } else if (delimiter === '|| ' || delimiter === '||') {
    delimiter = ' ';
  }
  
  return v.split(delimiter);
}

export function splitComma(v: any): any {
  return split(v, ',');
}

export function join(v: any, delimiter: string = ','): any {
  if (Array.isArray(v)) {
    return v.join(delimiter);
  }
  return v;
}

export function replace(v: any, oldStr: string, newStr: string): any {
  if (typeof v !== 'string') return v;
  // Escape special regex characters in oldStr for literal replacement
  const escapedOld = oldStr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return v.replace(new RegExp(escapedOld, 'g'), newStr);
}

export function replaceRegex(v: any, pattern: string, replacement: string): any {
  if (typeof v !== 'string') return v;
  try {
    return v.replace(new RegExp(pattern, 'g'), replacement);
  } catch {
    return v;
  }
}

export function prefix(v: any, prefixStr: string): any {
  if (v === null || v === undefined || v === '') return v;
  return `${prefixStr}${v}`;
}

export function suffix(v: any, suffixStr: string): any {
  if (v === null || v === undefined || v === '') return v;
  return `${v}${suffixStr}`;
}

export function slugify(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function toSnakeCase(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .replace(/([A-Z])/g, '_$1')
    .toLowerCase()
    .replace(/^_/, '')
    .replace(/\s+/g, '_');
}

export function toCamelCase(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .toLowerCase()
    .replace(/[^a-zA-Z0-9]+(.)/g, (_, char) => char.toUpperCase());
}

export function toPascalCase(v: any): any {
  if (typeof v !== 'string') return v;
  const camel = toCamelCase(v);
  return camel.charAt(0).toUpperCase() + camel.slice(1);
}

export function sanitizeFilename(v: any): any {
  if (typeof v !== 'string') return v;
  return v
    .replace(/[<>:"/\\|?*]/g, '')
    .replace(/\s+/g, '_')
    .substring(0, 255);
}
