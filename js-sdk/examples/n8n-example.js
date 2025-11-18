/**
 * n8n Custom Code Node Example
 * Use SaaStify Edge SDK in n8n workflows
 */

// Import the SDK (add @saastify/edge-sdk to package.json)
const { transform, validate, bulkApplyPipeRules } = require('@saastify/edge-sdk');

// ============================================
// Example 1: Transform product titles
// ============================================
function transformProductTitles() {
  // Get items from previous node
  const items = $input.all();
  
  return items.map(item => {
    const rawTitle = item.json.title;
    
    // Clean and format title
    const cleanedTitle = transform(rawTitle, 'strip + title_case + clean_html');
    
    return {
      json: {
        ...item.json,
        title: cleanedTitle,
        title_slug: transform(cleanedTitle, 'slugify'),
      }
    };
  });
}

// ============================================
// Example 2: Clean and validate prices
// ============================================
function cleanPrices() {
  const items = $input.all();
  
  return items.map(item => {
    const rawPrice = item.json.price;
    
    // Clean price: "$1,234.56" -> 1234.56
    const cleanedPrice = transform(rawPrice, 'clean_numeric_value + round_decimal|2');
    
    // Validate price
    const errors = validate(cleanedPrice, [
      {
        rule_type: 'required',
        field_name: 'price',
        params: {}
      },
      {
        rule_type: 'numeric_range',
        field_name: 'price',
        params: { min: 0, max: 100000 }
      }
    ]);
    
    return {
      json: {
        ...item.json,
        price: cleanedPrice,
        price_valid: errors.length === 0,
        price_errors: errors,
      }
    };
  });
}

// ============================================
// Example 3: Bulk transform multiple fields
// ============================================
function bulkTransformProducts() {
  const items = $input.all();
  
  return items.map(item => {
    const product = item.json;
    
    return {
      json: {
        // Transform SKU: uppercase, remove spaces, prefix
        sku: transform(product.sku, 'uppercase + remove_whitespace + prefix|SKU-'),
        
        // Transform title
        title: transform(product.title, 'strip + title_case'),
        
        // Transform description: clean HTML and truncate
        description: transform(product.description, 'clean_html + truncate|500'),
        
        // Clean price
        price: transform(product.price, 'clean_numeric_value + round_decimal|2'),
        
        // Transform tags: split, clean, and join
        tags: transform(product.tags, 'split|, + list_unique + list_sort'),
        
        // Format date
        created_date: transform(product.created_at, 'date_only'),
      }
    };
  });
}

// ============================================
// Example 4: Conditional transformations
// ============================================
function conditionalTransform() {
  const items = $input.all();
  
  return items.map(item => {
    const product = item.json;
    
    // Use if_empty for defaults
    const brand = transform(product.brand, 'if_empty|Unknown Brand');
    const color = transform(product.color, 'if_empty|Not Specified');
    
    // Calculate discount if sale price exists
    let discount = 0;
    if (product.sale_price && product.regular_price) {
      const regular = transform(product.regular_price, 'clean_numeric_value');
      const sale = transform(product.sale_price, 'clean_numeric_value');
      discount = ((regular - sale) / regular) * 100;
      discount = transform(discount, 'round_decimal|0');
    }
    
    return {
      json: {
        ...item.json,
        brand,
        color,
        discount_percentage: discount,
      }
    };
  });
}

// ============================================
// Example 5: Data validation workflow
// ============================================
function validateProductData() {
  const items = $input.all();
  
  const validItems = [];
  const invalidItems = [];
  
  items.forEach(item => {
    const product = item.json;
    
    // Validate all required fields
    const validationRules = {
      sku: [
        { rule_type: 'required', field_name: 'sku', params: {} },
        { rule_type: 'min_length', field_name: 'sku', params: { min: 3 } }
      ],
      title: [
        { rule_type: 'required', field_name: 'title', params: {} },
        { rule_type: 'max_length', field_name: 'title', params: { max: 200 } }
      ],
      price: [
        { rule_type: 'required', field_name: 'price', params: {} },
        { rule_type: 'numeric_range', field_name: 'price', params: { min: 0 } }
      ]
    };
    
    const allErrors = {};
    let hasErrors = false;
    
    for (const [field, rules] of Object.entries(validationRules)) {
      const errors = validate(product[field], rules);
      if (errors.length > 0) {
        allErrors[field] = errors;
        hasErrors = true;
      }
    }
    
    if (hasErrors) {
      invalidItems.push({
        json: {
          ...product,
          validation_errors: allErrors,
        }
      });
    } else {
      validItems.push(item);
    }
  });
  
  // Return both valid and invalid items
  // Use n8n's $node["NodeName"].json to access in next nodes
  return [
    { json: { valid_count: validItems.length, invalid_count: invalidItems.length } },
    ...validItems,
    ...invalidItems,
  ];
}

// ============================================
// Main execution - choose your function
// ============================================

// Uncomment the function you want to use:
// return transformProductTitles();
// return cleanPrices();
// return bulkTransformProducts();
// return conditionalTransform();
// return validateProductData();

// Default: simple transformation example
return $input.all().map(item => ({
  json: {
    ...item.json,
    processed_title: transform(item.json.title, 'strip + uppercase'),
  }
}));
