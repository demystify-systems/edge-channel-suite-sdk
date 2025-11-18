/**
 * SaaStify Edge SDK - TypeScript/JavaScript Implementation
 * Production-ready for Node.js, n8n, Vercel, and browser environments
 */

// Export core types
export * from './core/types';

// Export transformation operations
export {
  // Engine functions
  transform,
  bulkApplyPipeRules,
  parseRuleString,
  applyTransformations,
  getAvailableTransforms,
  hasTransform,
  // Module namespaces
  text,
  string,
  numeric,
  date,
  list,
  conditional,
  utility,
} from './transformations';

// Export validation operations
export {
  validate,
  validateRow,
  getAvailableValidators,
  hasValidator,
  rules,
} from './validation';

export const SDK_VERSION = '1.0.0';
export const SDK_STATUS = 'production-ready';

// Convenience re-exports for common use cases
import { transform as _transform } from './transformations';
import { validate as _validate } from './validation';

export const SaastifyEdge = {
  transform: _transform,
  validate: _validate,
  version: SDK_VERSION,
};
