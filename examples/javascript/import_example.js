/**
 * JavaScript Import Example
 * Demonstrates importing product data from CSV/XLSX/JSON/XML files
 */

const path = require('path');
const fs = require('fs').promises;
const { transform, bulkApplyPipeRules } = require('../../js-sdk/dist/transformations');
const { validateRow } = require('../../js-sdk/dist/validation');
const { getParser } = require('../../js-sdk/dist/core/parsers');

/**
 * Example 1: Basic CSV import with transformations
 */
async function exampleBasicImport() {
    console.log('\n=== Example 1: Basic CSV Import ===\n');
    
    // Sample CSV data (in real use, this would be a file)
    const csvData = `SKU,Product Name,Price,Description
SKU001,  wireless mouse  ,$29.99,"<p>Great mouse</p>"
SKU002,  USB CABLE  ,$9.99,"<b>High quality</b>"
SKU003,  keyboard  ,$49.99,"Mechanical keyboard"`;
    
    // Write sample data to temp file
    const tempFile = '/tmp/test_import.csv';
    await fs.writeFile(tempFile, csvData);
    
    // Parse CSV file
    const parser = getParser(tempFile);
    
    for await (const row of parser.parse(tempFile)) {
        console.log(`Row ${row.file_row_number}:`);
        console.log(`  Raw data:`, row.data);
        
        // Apply transformations
        const transformed = {
            sku: transform(row.data.SKU, 'strip + uppercase'),
            name: transform(row.data['Product Name'], 'strip + title_case'),
            price: transform(row.data.Price, 'clean_numeric_value + round_decimal|2'),
            description: transform(row.data.Description, 'clean_html + strip')
        };
        
        console.log(`  Transformed:`, transformed);
        
        // Validate
        const validations = {
            sku: [{ rule: 'required' }],
            name: [
                { rule: 'required' },
                { rule: 'min_length', args: { value: 3 } }
            ],
            price: [{ rule: 'numeric_range', args: { min: 0, max: 10000 } }]
        };
        
        const [isValid, errors, errorCount] = validateRow(transformed, validations);
        console.log(`  Valid: ${isValid}, Errors: ${errorCount}`);
        if (Object.keys(errors).length > 0) {
            console.log(`  Validation errors:`, errors);
        }
        console.log();
    }
    
    // Cleanup
    await fs.unlink(tempFile);
}

/**
 * Example 2: Bulk transformations with DSL
 */
async function exampleBulkTransformations() {
    console.log('\n=== Example 2: Bulk Transformations ===\n');
    
    // Sample product data
    const productNames = [
        '  wireless mouse  ',
        '  USB CABLE  ',
        '  mechanical keyboard  ',
        '  hdmi cable 4k  '
    ];
    
    const prices = ['$29.99', '$9.99', '$149.99', '$19.99'];
    const skus = ['WM-001', 'UC-002', 'KB-003', 'HC-004'];
    
    // Transform product names
    console.log('Transforming product names:');
    const cleanedNames = bulkApplyPipeRules(
        productNames,
        'strip + title_case'
    );
    productNames.forEach((original, i) => {
        console.log(`  '${original}' → '${cleanedNames[i]}'`);
    });
    
    // Transform prices
    console.log('\nTransforming prices:');
    const numericPrices = bulkApplyPipeRules(
        prices,
        'clean_numeric_value + round_decimal|2'
    );
    prices.forEach((original, i) => {
        console.log(`  '${original}' → ${numericPrices[i]}`);
    });
    
    // Generate slugs for URLs
    console.log('\nGenerating URL slugs:');
    const slugs = bulkApplyPipeRules(
        cleanedNames,
        'lowercase + replace| |-'
    );
    cleanedNames.forEach((name, i) => {
        console.log(`  '${name}' → '${slugs[i]}'`);
    });
    
    // Create full product objects
    console.log('\nFull product objects:');
    for (let i = 0; i < skus.length; i++) {
        const product = {
            sku: skus[i],
            name: cleanedNames[i],
            price: numericPrices[i],
            slug: slugs[i]
        };
        console.log(' ', product);
    }
}

/**
 * Example 3: Advanced transformations with multiple operations
 */
async function exampleAdvancedTransformations() {
    console.log('\n=== Example 3: Advanced Transformations ===\n');
    
    // Date transformations
    console.log('Date transformations:');
    const today = new Date();
    
    const formattedDate = transform(today, 'format_date|%Y-%m-%d');
    console.log(`  Formatted date: ${formattedDate}`);
    
    const futureDate = transform(today, 'add_days|30 + format_date|%Y-%m-%d');
    console.log(`  30 days from now: ${futureDate}`);
    
    // String manipulations
    console.log('\nString manipulations:');
    const brand = 'ACME Corp';
    const product = 'Wireless Mouse';
    
    const combined = transform(`${brand} ${product}`, 'uppercase + replace| |_');
    console.log(`  Combined: '${combined}'`);
    
    // Numeric operations
    console.log('\nNumeric operations:');
    const basePrice = 100.00;
    
    const discounted = transform(basePrice, 'multiplication|0.8 + round_decimal|2');
    console.log(`  20% discount: $${discounted}`);
    
    const withTax = transform(basePrice, 'multiplication|1.08 + round_decimal|2');
    console.log(`  With 8% tax: $${withTax}`);
    
    // Conditional transformations
    console.log('\nConditional transformations:');
    const emptyDescription = '';
    const description = transform(emptyDescription, 'if_empty|No description available');
    console.log(`  Empty description: '${description}'`);
}

/**
 * Example 4: Comprehensive validation
 */
async function exampleValidation() {
    console.log('\n=== Example 4: Validation Examples ===\n');
    
    // Test data
    const testProducts = [
        {
            sku: 'SKU001',
            name: 'Wireless Mouse',
            price: 29.99,
            email: 'contact@example.com',
            website: 'https://example.com',
            phone: '+1-555-123-4567'
        },
        {
            sku: '',  // Invalid: required
            name: 'KB',  // Invalid: too short
            price: 15000,  // Invalid: too expensive
            email: 'invalid-email',  // Invalid format
            website: 'not-a-url',  // Invalid format
            phone: '123'  // Invalid: too short
        }
    ];
    
    // Validation rules
    const validations = {
        sku: [
            { rule: 'required' }
        ],
        name: [
            { rule: 'required' },
            { rule: 'min_length', args: { value: 3 } },
            { rule: 'max_length', args: { value: 100 } }
        ],
        price: [
            { rule: 'required' },
            { rule: 'numeric_range', args: { min: 0, max: 10000 } }
        ],
        email: [
            { rule: 'email' }
        ],
        website: [
            { rule: 'url' }
        ],
        phone: [
            { rule: 'phone' }
        ]
    };
    
    // Validate each product
    testProducts.forEach((product, i) => {
        console.log(`Product ${i + 1}:`);
        console.log(`  Data:`, product);
        
        const [isValid, errors, errorCount] = validateRow(product, validations);
        
        console.log(`  Valid: ${isValid}`);
        if (Object.keys(errors).length > 0) {
            console.log(`  Errors (${errorCount}):`);
            for (const [field, fieldErrors] of Object.entries(errors)) {
                fieldErrors.forEach(error => {
                    console.log(`    - ${field}: ${error.message}`);
                });
            }
        }
        console.log();
    });
}

/**
 * Example 5: Working with different file formats
 */
async function exampleFileFormats() {
    console.log('\n=== Example 5: Multiple File Formats ===\n');
    
    // Sample data
    const products = [
        { sku: 'SKU001', name: 'Product 1', price: 29.99 },
        { sku: 'SKU002', name: 'Product 2', price: 49.99 },
    ];
    
    // JSON example
    console.log('JSON format:');
    const jsonFile = '/tmp/test_products.json';
    await fs.writeFile(jsonFile, JSON.stringify(products));
    
    const parser = getParser(jsonFile);
    let rowCount = 0;
    for await (const row of parser.parse(jsonFile)) {
        rowCount++;
        console.log(`  Row ${rowCount}:`, row.data);
    }
    
    await fs.unlink(jsonFile);
    
    console.log('\n✓ CSV, TSV, XLSX, JSON, and XML formats all supported!');
}

/**
 * Main function - run all examples
 */
async function main() {
    console.log('='.repeat(60));
    console.log('JavaScript SDK Import Examples');
    console.log('='.repeat(60));
    
    await exampleBasicImport();
    await exampleBulkTransformations();
    await exampleAdvancedTransformations();
    await exampleValidation();
    await exampleFileFormats();
    
    console.log('\n' + '='.repeat(60));
    console.log('All examples completed successfully!');
    console.log('='.repeat(60));
}

// Run if executed directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    exampleBasicImport,
    exampleBulkTransformations,
    exampleAdvancedTransformations,
    exampleValidation,
    exampleFileFormats
};
