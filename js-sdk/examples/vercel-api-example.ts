/**
 * Vercel Serverless Function Example
 * Deploy this as /api/transform-products.ts
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';
import { transform, validate, bulkApplyPipeRules } from '@saastify/edge-sdk';

/**
 * API endpoint to transform product data
 * POST /api/transform-products
 */
export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const { products, transformations } = req.body;
    
    if (!products || !Array.isArray(products)) {
      return res.status(400).json({ error: 'Invalid products array' });
    }
    
    // Transform products
    const transformedProducts = products.map((product) => {
      try {
        return {
          ...product,
          // Clean title
          title: transform(product.title || '', 'strip + title_case + clean_html'),
          
          // Generate slug
          slug: transform(product.title || '', 'slugify'),
          
          // Clean and validate price
          price: transform(product.price || '0', 'clean_numeric_value + round_decimal|2'),
          
          // Clean description
          description: transform(
            product.description || '',
            'clean_html + strip + truncate|1000'
          ),
          
          // Format SKU
          sku: transform(product.sku || '', 'uppercase + remove_whitespace'),
          
          // Process custom transformations if provided
          ...(transformations && applyCustomTransformations(product, transformations)),
        };
      } catch (error) {
        console.error('Error transforming product:', error);
        return {
          ...product,
          error: 'Transformation failed',
        };
      }
    });
    
    return res.status(200).json({
      success: true,
      count: transformedProducts.length,
      products: transformedProducts,
    });
  } catch (error: any) {
    console.error('API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message,
    });
  }
}

/**
 * Apply custom transformations based on config
 */
function applyCustomTransformations(product: any, config: Record<string, string>) {
  const result: Record<string, any> = {};
  
  for (const [field, rule] of Object.entries(config)) {
    try {
      result[field] = transform(product[field], rule);
    } catch (error) {
      result[field] = product[field]; // Keep original on error
    }
  }
  
  return result;
}
