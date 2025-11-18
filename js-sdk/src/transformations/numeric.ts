/**
 * Numeric transformation operations
 */

export function cleanNumericValue(v: any): any {
  if (typeof v === 'number') return v;
  if (typeof v !== 'string') return v;
  
  const cleaned = v.replace(/[$,\s]/g, '');
  const num = parseFloat(cleaned);
  return isNaN(num) ? v : num;
}

export function addition(v: any, amount: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num + amount;
}

export function subtraction(v: any, amount: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num - amount;
}

export function multiplication(v: any, factor: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : num * factor;
}

export function division(v: any, divisor: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num) || divisor === 0) return v;
  return num / divisor;
}

export function percentage(v: any, percent: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : (num * percent) / 100;
}

export function roundDecimal(v: any, decimals: number = 2): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return Number(num.toFixed(decimals));
}

export function absoluteValue(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : Math.abs(num);
}

export function ceiling(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : Math.ceil(num);
}

export function floor(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : Math.floor(num);
}

export function squareRoot(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) || num < 0 ? v : Math.sqrt(num);
}

export function power(v: any, exponent: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  return isNaN(num) ? v : Math.pow(num, exponent);
}

export function modulo(v: any, divisor: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num) || divisor === 0) return v;
  return num % divisor;
}

export function clamp(v: any, min: number, max: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return Math.min(Math.max(num, min), max);
}

export function scale(v: any, oldMin: number, oldMax: number, newMin: number, newMax: number): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return ((num - oldMin) / (oldMax - oldMin)) * (newMax - newMin) + newMin;
}

export function reciprocal(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num) || num === 0) return v;
  return 1 / num;
}

export function sign(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return Math.sign(num);
}

export function adjustNegativeToZero(v: any): any {
  const num = typeof v === 'number' ? v : parseFloat(v);
  if (isNaN(num)) return v;
  return num < 0 ? 0 : num;
}

export function zeroPadding(v: any, length: number): any {
  return String(v).padStart(length, '0');
}
