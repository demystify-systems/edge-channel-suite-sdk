/**
 * List/Array transformation operations
 */

export function listLength(v: any): any {
  return Array.isArray(v) ? v.length : v;
}

export function listFirst(v: any): any {
  return Array.isArray(v) && v.length > 0 ? v[0] : v;
}

export function listLast(v: any): any {
  return Array.isArray(v) && v.length > 0 ? v[v.length - 1] : v;
}

export function listUnique(v: any): any {
  if (!Array.isArray(v)) return v;
  return [...new Set(v)];
}

export function listSort(v: any, order: 'asc' | 'desc' = 'asc'): any {
  if (!Array.isArray(v)) return v;
  
  const sorted = [...v].sort((a, b) => {
    if (typeof a === 'number' && typeof b === 'number') {
      return a - b;
    }
    return String(a).localeCompare(String(b));
  });
  
  return order === 'desc' ? sorted.reverse() : sorted;
}
