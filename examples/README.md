# SaaStify Catalog Edge SDK - Examples

This directory contains comprehensive examples demonstrating how to use both the Python and JavaScript/TypeScript implementations of the Catalog Edge SDK.

## Directory Structure

```
examples/
├── README.md                    # This file
├── python/                      # Python examples
│   ├── import_example.py        # Import pipeline examples
│   └── export_example.py        # Export pipeline examples
└── javascript/                  # JavaScript/TypeScript examples
    ├── import_example.js        # Import pipeline examples
    └── export_example.js        # Export pipeline examples
```

## Overview

The Catalog Edge SDK provides a unified framework for:
- **Importing** product data from multiple file formats (CSV, TSV, XLSX, JSON, XML)
- **Transforming** data using 85 built-in operations via a powerful DSL
- **Validating** data with 14 validation rules
- **Exporting** data to multiple formats with channel-specific templates

Both Python and JavaScript implementations have **100% feature parity**.

## Quick Start

### Python Examples

#### Prerequisites
```bash
# Navigate to python-sdk
cd python-sdk

# Install dependencies
pip install -e .
```

#### Run Import Examples
```bash
# From the repository root
python3 examples/python/import_example.py
```

**What you'll learn:**
- Parsing CSV files with transformations
- Bulk transformations using the DSL
- Advanced string, numeric, and date operations
- Comprehensive validation with multiple rules
- Working with different file formats

#### Run Export Examples
```bash
# From the repository root
python3 examples/python/export_example.py
```

**What you'll learn:**
- Exporting to CSV, XLSX, JSON, and XML
- Complex transformation pipelines
- Channel-specific exports (Amazon, Shopify, etc.)
- Calculating derived fields (discounts, slugs)

### JavaScript Examples

#### Prerequisites
```bash
# Navigate to js-sdk
cd js-sdk

# Install dependencies
npm install

# Build the SDK
npm run build
```

#### Run Import Examples
```bash
# From the repository root
node examples/javascript/import_example.js
```

**What you'll learn:**
- Parsing CSV files with transformations
- Bulk transformations using the DSL
- Advanced string, numeric, and date operations
- Comprehensive validation with multiple rules
- Working with different file formats

#### Run Export Examples
```bash
# From the repository root
node examples/javascript/export_example.js
```

**What you'll learn:**
- Exporting to CSV, XLSX, JSON, and XML
- Complex transformation pipelines
- Channel-specific exports (Amazon, Shopify, etc.)
- Calculating derived fields (discounts, slugs)

## Example Use Cases

### 1. Basic Import with Transformations

Import a CSV file, clean the data, and validate it:

**Python:**
```python
from saastify_edge.transformations import transform
from saastify_edge.validation import validate_row
from saastify_edge.core.parsers import get_parser

# Parse CSV
parser = get_parser('products.csv')
async for row in parser.parse('products.csv'):
    # Transform
    transformed = {
        'sku': transform(row['data']['SKU'], 'strip + uppercase'),
        'name': transform(row['data']['Name'], 'strip + title_case'),
        'price': transform(row['data']['Price'], 'clean_numeric_value + round_decimal|2')
    }
    
    # Validate
    validations = {
        'sku': [{'rule': 'required'}],
        'price': [{'rule': 'numeric_range', 'args': {'min': 0, 'max': 10000}}]
    }
    is_valid, errors, error_count = validate_row(transformed, validations)
```

**JavaScript:**
```javascript
const { transform } = require('./js-sdk/dist/transformations');
const { validateRow } = require('./js-sdk/dist/validation');
const { getParser } = require('./js-sdk/dist/core/parsers');

// Parse CSV
const parser = getParser('products.csv');
for await (const row of parser.parse('products.csv')) {
    // Transform
    const transformed = {
        sku: transform(row.data.SKU, 'strip + uppercase'),
        name: transform(row.data.Name, 'strip + title_case'),
        price: transform(row.data.Price, 'clean_numeric_value + round_decimal|2')
    };
    
    // Validate
    const validations = {
        sku: [{ rule: 'required' }],
        price: [{ rule: 'numeric_range', args: { min: 0, max: 10000 } }]
    };
    const [isValid, errors, errorCount] = validateRow(transformed, validations);
}
```

### 2. Bulk Transformations

Apply transformations to multiple values at once:

**Python:**
```python
from saastify_edge.transformations import bulk_apply_pipe_rules

# Transform multiple product names
product_names = ['  wireless mouse  ', '  USB CABLE  ', '  keyboard  ']
cleaned = bulk_apply_pipe_rules(product_names, 'strip + title_case')
# Result: ['Wireless Mouse', 'Usb Cable', 'Keyboard']

# Transform prices
prices = ['$29.99', '$9.99', '$149.99']
numeric = bulk_apply_pipe_rules(prices, 'clean_numeric_value + round_decimal|2')
# Result: [29.99, 9.99, 149.99]
```

**JavaScript:**
```javascript
const { bulkApplyPipeRules } = require('./js-sdk/dist/transformations');

// Transform multiple product names
const productNames = ['  wireless mouse  ', '  USB CABLE  ', '  keyboard  '];
const cleaned = bulkApplyPipeRules(productNames, 'strip + title_case');
// Result: ['Wireless Mouse', 'Usb Cable', 'Keyboard']

// Transform prices
const prices = ['$29.99', '$9.99', '$149.99'];
const numeric = bulkApplyPipeRules(prices, 'clean_numeric_value + round_decimal|2');
// Result: [29.99, 9.99, 149.99]
```

### 3. Export to Multiple Formats

Export products to CSV, XLSX, JSON, or XML:

**Python:**
```python
from saastify_edge.export import build_csv, build_xlsx, build_json, build_xml

products = [
    {'sku': 'SKU001', 'name': 'Wireless Mouse', 'price': 29.99},
    {'sku': 'SKU002', 'name': 'USB Cable', 'price': 9.99}
]

# CSV
csv_config = {'format': 'csv', 'delimiter': ',', 'include_headers': True}
csv_content = build_csv(products, csv_config)

# XLSX
xlsx_config = {'format': 'xlsx', 'sheet_name': 'Products'}
xlsx_bytes = build_xlsx(products, xlsx_config)

# JSON
json_config = {'format': 'json', 'pretty': True}
json_content = build_json(products, json_config)

# XML
xml_config = {'format': 'xml', 'root_element': 'products'}
xml_content = build_xml(products, xml_config)
```

**JavaScript:**
```javascript
const { buildCSV, buildXLSX, buildJSON, buildXML } = require('./js-sdk/dist/export');

const products = [
    { sku: 'SKU001', name: 'Wireless Mouse', price: 29.99 },
    { sku: 'SKU002', name: 'USB Cable', price: 9.99 }
];

// CSV
const csvConfig = { format: 'csv', delimiter: ',', include_headers: true };
const csvContent = buildCSV(products, csvConfig);

// XLSX
const xlsxConfig = { format: 'xlsx', sheet_name: 'Products' };
const xlsxBuffer = buildXLSX(products, xlsxConfig);

// JSON
const jsonConfig = { format: 'json', pretty: true };
const jsonContent = buildJSON(products, jsonConfig);

// XML
const xmlConfig = { format: 'xml', root_element: 'products' };
const xmlContent = buildXML(products, xmlConfig);
```

### 4. Channel-Specific Export (Amazon)

Export products in Amazon's required format:

**Python:**
```python
from saastify_edge.transformations import transform
from saastify_edge.export import build_csv

# Transform for Amazon
amazon_product = {
    'seller_sku': transform(product['sku'], 'uppercase'),
    'product_name': transform(product['title'], 'title_case'),
    'product_id': transform(product['upc'], 'clean_upc'),
    'product_id_type': 'UPC',
    'standard_price': transform(product['price'], 'round_decimal|2'),
    'quantity': 999
}

# Export as TSV (Amazon format)
config = {
    'format': 'tsv',
    'delimiter': '\t',
    'columns': ['seller_sku', 'product_name', 'product_id', 'standard_price']
}
tsv_content = build_csv([amazon_product], config)
```

**JavaScript:**
```javascript
const { transform } = require('./js-sdk/dist/transformations');
const { buildCSV } = require('./js-sdk/dist/export');

// Transform for Amazon
const amazonProduct = {
    seller_sku: transform(product.sku, 'uppercase'),
    product_name: transform(product.title, 'title_case'),
    product_id: transform(product.upc, 'clean_upc'),
    product_id_type: 'UPC',
    standard_price: transform(product.price, 'round_decimal|2'),
    quantity: 999
};

// Export as TSV (Amazon format)
const config = {
    format: 'tsv',
    delimiter: '\t',
    columns: ['seller_sku', 'product_name', 'product_id', 'standard_price']
};
const tsvContent = buildCSV([amazonProduct], config);
```

## Transformation DSL

The SDK uses a powerful DSL for transformations:

### Syntax

- **Chaining**: Use ` + ` to chain operations
  ```
  'strip + uppercase + replace| |-'
  ```

- **Parameters**: Use `|` to separate parameters
  ```
  'split|,'
  'replace|old|new'
  'vlookup|key1:val1,key2:val2'
  ```

### Available Operations (85 total)

#### Text Operations
- `uppercase`, `lowercase`, `capitalize`, `title_case`
- `strip`, `lstrip`, `rstrip`
- `split`, `join`, `concat`
- `replace`, `replace_regex`
- `prefix`, `suffix`
- `clean_html`, `xml_escape`, `html_unescape`
- `url_encode`, `url_decode`
- `base64_encode`, `base64_decode`

#### Numeric Operations
- `clean_numeric_value`
- `addition`, `subtraction`, `multiplication`, `division`
- `percentage`, `round_decimal`, `ceil`, `floor`
- `abs_value`, `adjust_negative_to_zero`
- `zero_padding`

#### Date Operations
- `date_only`, `format_date`, `parse_date`
- `add_days`, `subtract_days`
- `add_months`, `subtract_months`
- `date_diff`, `is_before`, `is_after`

#### Conditional Operations
- `if_empty`, `if_null`, `coalesce`
- `if_equals`, `if_contains`

#### Lookup Operations
- `vlookup_map` - Dictionary-based lookup

#### Utility Operations
- `md5_hash`, `json_parse`, `json_stringify`
- `currency_format`, `levenshtein_distance`
- `extract_domain`, `string_similarity`

## Validation Rules (14 total)

### Available Rules

1. **required** - Value must not be empty
2. **min_length** - Minimum string length
3. **max_length** - Maximum string length
4. **regex** - Must match pattern
5. **enum** - Must be in allowed values
6. **numeric_range** - Number within min/max
7. **date_before** - Date before specified date
8. **date_after** - Date after specified date
9. **email** - Valid email format
10. **url** - Valid URL format
11. **phone** - Valid phone number
12. **credit_card** - Valid credit card format
13. **ip_address** - Valid IP address
14. **custom_expression** - Custom validation logic

### Example Validation Configuration

```python
validations = {
    'sku': [
        {'rule': 'required'},
        {'rule': 'min_length', 'args': {'value': 3}}
    ],
    'name': [
        {'rule': 'required'},
        {'rule': 'max_length', 'args': {'value': 100}}
    ],
    'price': [
        {'rule': 'numeric_range', 'args': {'min': 0, 'max': 10000}}
    ],
    'email': [
        {'rule': 'email'}
    ],
    'website': [
        {'rule': 'url'}
    ]
}
```

## File Format Support

Both SDKs support the following formats:

### Import (Read)
- ✅ CSV (comma-separated)
- ✅ TSV (tab-separated)
- ✅ XLSX (Excel)
- ✅ JSON (array or line-delimited)
- ✅ XML (with configurable element names)

### Export (Write)
- ✅ CSV (comma-separated)
- ✅ TSV (tab-separated)
- ✅ XLSX (Excel with multiple sheets)
- ✅ JSON (formatted or compact)
- ✅ XML (with configurable structure)

## Using in Your Projects

### Python

#### Install from local directory
```bash
cd python-sdk
pip install -e .
```

#### Use in your code
```python
from saastify_edge.transformations import transform, bulk_apply_pipe_rules
from saastify_edge.validation import validate_row
from saastify_edge.core.parsers import get_parser
from saastify_edge.export import build_csv, build_xlsx

# Your code here
```

### JavaScript/TypeScript

#### Install from local directory
```bash
cd js-sdk
npm install
npm run build
npm link
```

#### Use in your project
```bash
cd your-project
npm link @saastify/edge-sdk
```

#### Import in your code
```javascript
// CommonJS
const { transform, bulkApplyPipeRules } = require('@saastify/edge-sdk/transformations');
const { validateRow } = require('@saastify/edge-sdk/validation');

// ES Modules
import { transform, bulkApplyPipeRules } from '@saastify/edge-sdk/transformations';
import { validateRow } from '@saastify/edge-sdk/validation';
```

## Advanced Usage

### Custom Transformation Pipelines

Create reusable transformation pipelines:

**Python:**
```python
# Define pipeline for product names
name_pipeline = 'strip + title_case + replace| |-'

# Apply to multiple products
for product in products:
    product['name'] = transform(product['name'], name_pipeline)
```

**JavaScript:**
```javascript
// Define pipeline for product names
const namePipeline = 'strip + title_case + replace| |-';

// Apply to multiple products
products.forEach(product => {
    product.name = transform(product.name, namePipeline);
});
```

### Combining Multiple Validations

Stack multiple validation rules:

```python
validations = {
    'sku': [
        {'rule': 'required'},
        {'rule': 'regex', 'args': {'pattern': '^[A-Z0-9-]+$'}},
        {'rule': 'min_length', 'args': {'value': 5}},
        {'rule': 'max_length', 'args': {'value': 20}}
    ]
}
```

## Integration Examples

### N8N Workflow (JavaScript)

```javascript
// N8N Function Node
const { transform } = require('@saastify/edge-sdk/transformations');

const items = $input.all();

return items.map(item => ({
    json: {
        sku: transform(item.json.sku, 'strip + uppercase'),
        name: transform(item.json.name, 'strip + title_case'),
        price: transform(item.json.price, 'clean_numeric_value + round_decimal|2')
    }
}));
```

### Vercel Edge Function (JavaScript)

```javascript
// api/transform.js
import { transform } from '@saastify/edge-sdk/transformations';

export default async function handler(req, res) {
    const { data, rules } = req.body;
    
    const transformed = data.map(item => ({
        ...item,
        name: transform(item.name, rules.name),
        price: transform(item.price, rules.price)
    }));
    
    res.json({ transformed });
}
```

### Flask API (Python)

```python
# app.py
from flask import Flask, request, jsonify
from saastify_edge.transformations import transform

app = Flask(__name__)

@app.route('/transform', methods=['POST'])
def transform_data():
    data = request.json['data']
    rules = request.json['rules']
    
    transformed = [
        {
            **item,
            'name': transform(item['name'], rules['name']),
            'price': transform(item['price'], rules['price'])
        }
        for item in data
    ]
    
    return jsonify({'transformed': transformed})
```

## Troubleshooting

### Python Issues

**Import errors:**
```bash
# Make sure SDK is installed
pip install -e python-sdk/
```

**Missing dependencies:**
```bash
# Install all dependencies
cd python-sdk
pip install -r requirements.txt
```

### JavaScript Issues

**Module not found:**
```bash
# Build the SDK first
cd js-sdk
npm run build
```

**Type errors (TypeScript):**
```bash
# Run type checking
npm run typecheck
```

## Performance Tips

1. **Batch transformations** - Use `bulk_apply_pipe_rules` for multiple values
2. **Reuse parsers** - Cache parser instances when processing multiple files
3. **Stream large files** - Use async iterators to process files row-by-row
4. **Validate once** - Validate during import, reuse cache for export

## Support

For more information:
- **Documentation**: See `/docs` folder in repository
- **Issues**: GitHub Issues
- **API Reference**: See `AI_AGENT_GUIDE.md`

## License

Copyright © 2024 SaaStify. All rights reserved.
