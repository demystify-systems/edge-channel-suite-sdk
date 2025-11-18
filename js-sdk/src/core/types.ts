/**
 * Core type definitions for SaaStify Edge SDK
 * Matches Python SDK types for transformation parity
 */

export interface TransformationStep {
  operation: string;
  args: Record<string, any>;
}

export interface ValidationRule {
  rule_type: string;
  field_name: string;
  params: Record<string, any>;
  error_message?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  rule_type: string;
  value?: any;
}

export interface TemplateAttribute {
  name: string;
  data_type: string;
  transformations: TransformationStep[];
  validations: ValidationRule[];
  required?: boolean;
  default_value?: any;
}

export interface ChannelTemplate {
  template_id: string;
  channel_name: string;
  attributes: TemplateAttribute[];
  column_mappings?: Record<string, string>;
}

export interface FileConfig {
  format: 'csv' | 'tsv' | 'xlsx' | 'json' | 'xml';
  delimiter?: string;
  has_headers?: boolean;
  sheet_name?: string;
  encoding?: string;
}

export interface TransformedRow {
  [key: string]: any;
}

export interface ImportResult {
  job_id: string;
  total_rows: number;
  valid_count: number;
  rejected_count: number;
  error_count: number;
  transformed_data: TransformedRow[];
  validation_errors: Record<string, ValidationError[]>;
}

export interface ExportResult {
  job_id: string;
  exported_count: number;
  output_path: string;
  file_size: number;
}

export interface ImportPipelineConfig {
  file_source: string;
  template_id: string;
  saas_edge_id: string;
  file_format?: string;
  batch_size?: number;
  max_workers?: number;
}

export interface ExportPipelineConfig {
  template_id: string;
  saas_edge_id: string;
  output_format: string;
  output_path: string;
  product_ids?: string[];
  use_cache?: boolean;
}

export interface JobMetrics {
  stage: string;
  start_time: Date;
  end_time?: Date;
  duration_ms?: number;
  rows_processed?: number;
  errors?: number;
}

export type TransformFn = (value: any, ...args: any[]) => any;
export type ValidatorFn = (value: any, params: Record<string, any>) => boolean;

/**
 * Special exception for rejecting rows during transformation
 */
export class RejectRow extends Error {
  constructor(message?: string) {
    super(message || 'Row rejected during transformation');
    this.name = 'RejectRow';
  }
}
