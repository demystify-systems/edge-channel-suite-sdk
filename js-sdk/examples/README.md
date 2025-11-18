# SaaStify Edge SDK - Usage Examples

This directory contains real-world examples for using the SDK in different environments.

## Table of Contents

- [n8n Workflows](#n8n-workflows)
- [Vercel Serverless Functions](#vercel-serverless-functions)
- [Node.js Scripts](#nodejs-scripts)
- [Browser Usage](#browser-usage)

## n8n Workflows

### Setup

1. In your n8n instance, go to **Settings** → **Community Nodes**
2. Install `@saastify/edge-sdk`
3. Create a **Code** node
4. Copy code from `n8n-example.js`

### Available Examples

**Example 1: Transform Product Titles**
```javascript
const { transform } = require('@saastify/edge-sdk');
const cleanTitle = transform(rawTitle, 'strip + title_case + clean_html');
```

**Example 2: Clean and Validate Prices**
```javascript
const { transform, validate } = require('@saastify/edge-sdk');
const price = transform(rawPrice, 'clean_numeric_value + round_decimal|2');
const errors = validate(price, [/* validation rules */]);
```

**Example 3: Bulk Transform Multiple Fields**
- SKU formatting
- Title cleaning
- Description truncation
- Price cleaning
- Tag processing
- Date formatting

**Example 4: Conditional Transformations**
- Default values with `if_empty`
- Discount calculations
- Conditional field processing

**Example 5: Data Validation Workflow**
- Multi-field validation
- Splitting valid/invalid items
- Error collection

### n8n Workflow Tips

1. **Install the package**:
   - Add `@saastify/edge-sdk` in n8n settings
   - Or use `npm install @saastify/edge-sdk` in your n8n installation

2. **Access data from previous nodes**:
   ```javascript
   const items = $input.all(); // Get all items
   const firstItem = $input.first(); // Get first item
   ```

3. **Return data to next nodes**:
   ```javascript
   return items.map(item => ({
     json: { ...transformedData }
   }));
   ```

4. **Error handling**:
   ```javascript
   try {
     const result = transform(value, rule);
   } catch (error) {
     console.error('Transform error:', error);
     // Handle error
   }
   ```

## Vercel Serverless Functions

### Setup

1. Create a Vercel project
2. Install the SDK:
   ```bash
   npm install @saastify/edge-sdk
   ```
3. Create `api/transform-products.ts`
4. Deploy to Vercel

### API Usage

**Endpoint**: `POST /api/transform-products`

**Request Body**:
```json
{
  "products": [
    {
      "title": "  iPhone 15 Pro  ",
      "price": "$1,299.99",
      "description": "<p>Latest iPhone</p>",
      "sku": "iph 15 pro"
    }
  ],
  "transformations": {
    "custom_field": "uppercase + strip"
  }
}
```

**Response**:
```json
{
  "success": true,
  "count": 1,
  "products": [
    {
      "title": "Iphone 15 Pro",
      "slug": "iphone-15-pro",
      "price": 1299.99,
      "description": "Latest iPhone",
      "sku": "IPH15PRO",
      "custom_field": "TRANSFORMED VALUE"
    }
  ]
}
```

### Vercel Environment

The SDK works in:
- ✅ Edge Functions (Vercel Edge Runtime)
- ✅ Serverless Functions (Node.js runtime)
- ✅ Static Site Generation (SSG)
- ✅ Server-Side Rendering (SSR)

## Node.js Scripts

### Simple Transformation Script

```javascript
const { transform, bulkApplyPipeRules } = require('@saastify/edge-sdk');

// Single transformation
const result = transform('  hello world  ', 'strip + uppercase');
console.log(result); // "HELLO WORLD"

// Bulk transformation
const products = ['product 1', 'product 2', 'product 3'];
const cleaned = bulkApplyPipeRules(products, 'title_case + slugify');
console.log(cleaned); // ["Product 1", "Product 2", "Product 3"]
```

### File Processing Script

```javascript
const fs = require('fs');
const { transform } = require('@saastify/edge-sdk');

// Read CSV file
const data = fs.readFileSync('products.csv', 'utf-8');
const lines = data.split('\n');

// Transform each line
const transformed = lines.map(line => {
  const [sku, title, price] = line.split(',');
  return {
    sku: transform(sku, 'uppercase + strip'),
    title: transform(title, 'strip + title_case'),
    price: transform(price, 'clean_numeric_value'),
  };
});

// Write output
fs.writeFileSync('products-clean.json', JSON.stringify(transformed, null, 2));
```

## Browser Usage

### CDN (unpkg)

```html
<script src="https://unpkg.com/@saastify/edge-sdk@latest/dist/index.js"></script>
<script>
  const { transform, validate } = SaastifyEdge;
  
  // Transform user input
  const input = document.getElementById('title').value;
  const cleaned = transform(input, 'strip + title_case');
  document.getElementById('output').value = cleaned;
</script>
```

### ES Modules

```html
<script type="module">
  import { transform } from 'https://unpkg.com/@saastify/edge-sdk@latest/dist/index.js';
  
  const result = transform('hello', 'uppercase');
  console.log(result); // "HELLO"
</script>
```

### React/Vue/Angular

```javascript
import { transform, validate } from '@saastify/edge-sdk';

function ProductForm() {
  const handleTransform = (value) => {
    return transform(value, 'strip + title_case');
  };
  
  const handleValidate = (value) => {
    return validate(value, [
      { rule_type: 'required', field_name: 'title', params: {} }
    ]);
  };
  
  return (/* your component */);
}
```

## Common Transformation Patterns

### Product Data Cleaning

```javascript
const { transform } = require('@saastify/edge-sdk');

const product = {
  sku: '  abc-123  ',
  title: '<p>  Widget Pro  </p>',
  price: '$1,234.56',
  description: '<div>Great product!  </div>',
};

const cleaned = {
  sku: transform(product.sku, 'strip + uppercase'),
  title: transform(product.title, 'clean_html + strip + title_case'),
  price: transform(product.price, 'clean_numeric_value'),
  description: transform(product.description, 'clean_html + strip + truncate|500'),
};
```

### URL Slug Generation

```javascript
const title = 'iPhone 15 Pro (128GB) - Blue';
const slug = transform(title, 'slugify');
// Output: "iphone-15-pro-128gb-blue"
```

### Price Formatting

```javascript
const prices = ['$1,234', '€999.99', '£500'];
const cleaned = bulkApplyPipeRules(
  prices,
  'clean_numeric_value + round_decimal|2'
);
// Output: [1234, 999.99, 500]
```

### Text Normalization

```javascript
const text = '  Café Münchën  ';
const normalized = transform(
  text,
  'strip + lowercase + remove_accents + to_snake_case'
);
// Output: "cafe_munchen"
```

## Testing

### Unit Testing (Jest)

```javascript
const { transform } = require('@saastify/edge-sdk');

describe('Product transformations', () => {
  test('should clean SKU', () => {
    expect(transform('  abc-123  ', 'strip + uppercase')).toBe('ABC-123');
  });
  
  test('should format price', () => {
    expect(transform('$1,234.56', 'clean_numeric_value')).toBe(1234.56);
  });
});
```

## Performance Tips

1. **Reuse parsed rules**: Parse rule strings once and reuse
   ```javascript
   const { parseRuleString, applyTransformations } = require('@saastify/edge-sdk');
   const steps = parseRuleString('strip + uppercase'); // Parse once
   
   // Apply to many values
   values.forEach(v => applyTransformations(v, steps));
   ```

2. **Use bulk operations**: For multiple values with same rule
   ```javascript
   const results = bulkApplyPipeRules(values, 'strip + uppercase');
   ```

3. **Avoid complex transformations in loops**: Pre-process if possible

## Troubleshooting

### Module not found

If you get "Cannot find module '@saastify/edge-sdk'":
- Run `npm install @saastify/edge-sdk`
- Check your `package.json` dependencies

### Transformation not working

1. Check operation name (use underscore, not camelCase):
   - ✅ `title_case`
   - ❌ `titleCase`

2. Verify parameters are correct:
   - ✅ `truncate|100`
   - ❌ `truncate(100)`

3. Check for proper spacing in DSL:
   - ✅ `strip + uppercase`
   - ❌ `strip+uppercase`

### TypeScript errors

If using TypeScript, install type definitions:
```bash
npm install --save-dev @types/node
```

## Support

- **Documentation**: See main README.md
- **GitHub**: https://github.com/saastify/edge-sdk
- **Issues**: https://github.com/saastify/edge-sdk/issues

## License

MIT
