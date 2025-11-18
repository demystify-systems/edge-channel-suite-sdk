/**
 * Date transformation operations
 */

function toDate(v: any): Date | null {
  if (v instanceof Date) return v;
  if (typeof v === 'string' || typeof v === 'number') {
    const date = new Date(v);
    return isNaN(date.getTime()) ? null : date;
  }
  return null;
}

export function dateOnly(v: any): any {
  const date = toDate(v);
  return date ? date.toISOString().split('T')[0] : v;
}

export function formatDate(v: any, format: string = '%Y-%m-%d'): any {
  const date = toDate(v);
  if (!date) return v;
  
  // Simple format string replacement (subset of strftime)
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  const second = String(date.getSeconds()).padStart(2, '0');
  
  return format
    .replace('%Y', String(year))
    .replace('%m', month)
    .replace('%d', day)
    .replace('%H', hour)
    .replace('%M', minute)
    .replace('%S', second);
}

export function addDays(v: any, days: number): any {
  const date = toDate(v);
  if (!date) return v;
  
  const newDate = new Date(date);
  newDate.setDate(newDate.getDate() + days);
  return newDate.toISOString();
}

export function subtractDays(v: any, days: number): any {
  return addDays(v, -days);
}

export function dayOfWeek(v: any): any {
  const date = toDate(v);
  return date ? date.getDay() : v; // 0 = Sunday, 6 = Saturday
}

export function dayName(v: any): any {
  const date = toDate(v);
  if (!date) return v;
  
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[date.getDay()];
}

export function monthName(v: any): any {
  const date = toDate(v);
  if (!date) return v;
  
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[date.getMonth()];
}

export function year(v: any): any {
  const date = toDate(v);
  return date ? date.getFullYear() : v;
}

export function month(v: any): any {
  const date = toDate(v);
  return date ? date.getMonth() + 1 : v; // 1-12
}

export function day(v: any): any {
  const date = toDate(v);
  return date ? date.getDate() : v; // 1-31
}

export function isWeekend(v: any): any {
  const date = toDate(v);
  if (!date) return v;
  
  const dayOfWeek = date.getDay();
  return dayOfWeek === 0 || dayOfWeek === 6;
}

export function daysBetween(v: any, otherDate: string): any {
  const date1 = toDate(v);
  const date2 = toDate(otherDate);
  
  if (!date1 || !date2) return v;
  
  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}
