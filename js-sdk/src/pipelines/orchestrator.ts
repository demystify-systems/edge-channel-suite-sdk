/**
 * Simple Import/Export Orchestrator
 * Lightweight pipeline for basic use cases
 */

import { transform, bulkApplyPipeRules } from '../transformations';
import { validate, validateRow } from '../validation';
import { parseFile } from '../core/parsers';
import { buildFile, writeFile } from '../export/builders';
import type { ValidationRule, ValidationError } from '../core/types';

export interface PipelineConfig {
  transformations?: Record<string, string>; // field -> rule string
  validations?: Record<string, ValidationRule[]>; // field -> validation rules
}

export interface ImportResult {
  totalRows: number;
  validRows: number;
  invalidRows: number;
  data: Record<string, any>[];
  errors: Record<string, Record<string, ValidationError[]>>;
}

export interface ExportResult {
  rowCount: number;
  outputPath?: string;
  content: string;
}

/**
 * Import and transform data from a file
 */
export async function runImport(
  filePath: string,
  config: PipelineConfig = {}
): Promise<ImportResult> {
  // Parse file
  const rows = await parseFile(filePath);
  
  const result: ImportResult = {
    totalRows: rows.length,
    validRows: 0,
    invalidRows: 0,
    data: [],
    errors: {},
  };
  
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const transformedRow: Record<string, any> = {};
    
    // Apply transformations
    if (config.transformations) {
      for (const [field, rule] of Object.entries(config.transformations)) {
        try {
          transformedRow[field] = transform(row[field], rule);
        } catch {
          transformedRow[field] = row[field];
        }
      }
    } else {
      Object.assign(transformedRow, row);
    }
    
    // Apply validations
    let hasErrors = false;
    if (config.validations) {
      const rowErrors = validateRow(transformedRow, config.validations);
      
      if (Object.keys(rowErrors).length > 0) {
        result.errors[`row_${i}`] = rowErrors;
        hasErrors = true;
      }
    }
    
    if (hasErrors) {
      result.invalidRows++;
    } else {
      result.validRows++;
      result.data.push(transformedRow);
    }
  }
  
  return result;
}

/**
 * Transform and export data to a file
 */
export async function runExport(
  data: Record<string, any>[],
  outputPath: string,
  format: 'csv' | 'tsv' | 'json' | 'xml',
  config: PipelineConfig = {}
): Promise<ExportResult> {
  const transformedData: Record<string, any>[] = [];
  
  for (const row of data) {
    const transformedRow: Record<string, any> = {};
    
    // Apply transformations
    if (config.transformations) {
      for (const [field, rule] of Object.entries(config.transformations)) {
        try {
          transformedRow[field] = transform(row[field], rule);
        } catch {
          transformedRow[field] = row[field];
        }
      }
    } else {
      Object.assign(transformedRow, row);
    }
    
    transformedData.push(transformedRow);
  }
  
  // Build file content
  const content = buildFile(transformedData, { format });
  
  // Write to file (Node.js only)
  try {
    await writeFile(outputPath, content);
  } catch {
    // Silently continue if not in Node.js environment
  }
  
  return {
    rowCount: transformedData.length,
    outputPath,
    content,
  };
}

/**
 * Transform data in memory (no file I/O)
 */
export function transformData(
  data: Record<string, any>[],
  config: PipelineConfig
): Record<string, any>[] {
  return data.map(row => {
    const transformed: Record<string, any> = {};
    
    if (config.transformations) {
      for (const [field, rule] of Object.entries(config.transformations)) {
        try {
          transformed[field] = transform(row[field], rule);
        } catch {
          transformed[field] = row[field];
        }
      }
    } else {
      Object.assign(transformed, row);
    }
    
    return transformed;
  });
}

/**
 * Validate data without transformation
 */
export function validateData(
  data: Record<string, any>[],
  validations: Record<string, ValidationRule[]>
): { valid: Record<string, any>[]; invalid: Record<string, any>[]; errors: Record<string, Record<string, ValidationError[]>> } {
  const valid: Record<string, any>[] = [];
  const invalid: Record<string, any>[] = [];
  const errors: Record<string, Record<string, ValidationError[]>> = {};
  
  data.forEach((row, i) => {
    const rowErrors = validateRow(row, validations);
    
    if (Object.keys(rowErrors).length > 0) {
      errors[`row_${i}`] = rowErrors;
      invalid.push(row);
    } else {
      valid.push(row);
    }
  });
  
  return { valid, invalid, errors };
}
