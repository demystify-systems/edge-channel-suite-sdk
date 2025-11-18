/**
 * JavaScript Export Example
 * Demonstrates exporting product data to CSV/XLSX/JSON/XML files
 */

const fs = require('fs').promises;
const { transform, bulkApplyPipeRules } = require('../../js-sdk/dist/transformations');
const { buildCSV, buildXLSX, buildJSON, buildXML } = require('../../js-sdk/dist/export');

/**
 * Example 1: Export products to CSV
 */
async function exampleCSVExport() {
    console.log('\n=== Example 1: CSV Export ===\n');
    
    // Sample product data
    const products = [
        {
            sku: 'SKU001',
            name: 'Wireless Mouse',
            price: 29.99,
            description: 'Ergonomic wireless mouse with USB receiver'
        },
        {
            sku: 'SKU002',
            name: 'USB Cable',
            price: 9.99,
            description: 'High-quality USB-C cable'
        },
        {
            sku: 'SKU003',
            name: 'Mechanical Keyboard',
            price: 149.99,
            description: 'Cherry MX Blue switches'
        }
    ];
    
    // Configure CSV export
    const fileConfig = {
        format: 'csv',
        delimiter: ',',
        include_headers: true,
        columns: ['sku', 'name', 'price', 'description']
    };
    
    // Apply transformations before export
    const transformedProducts = products.map(product => ({
        sku: transform(product.sku, 'uppercase'),
        name: transform(product.name, 'title_case'),
        price: transform(product.price, 'round_decimal|2'),
        description: product.description
    }));
    
    // Build CSV
    const csvContent = buildCSV(transformedProducts, fileConfig);
    
    console.log('Generated CSV:');
    console.log(csvContent);
    
    // Save to file
    const outputPath = '/tmp/products_export.csv';
    await fs.writeFile(outputPath, csvContent);
    
    console.log(`\n✓ Exported to ${outputPath}`);
}

/**
 * Example 2: Export products to Excel (XLSX)
 */
async function exampleXLSXExport() {
    console.log('\n=== Example 2: XLSX Export ===\n');
    
    // Sample product data
    const products = [
        {
            sku: 'SKU001',
            name: 'Wireless Mouse',
            category: 'Electronics',
            price: 29.99,
            stock: 150
        },
        {
            sku: 'SKU002',
            name: 'USB Cable',
            category: 'Accessories',
            price: 9.99,
            stock: 500
        },
        {
            sku: 'SKU003',
            name: 'Mechanical Keyboard',
            category: 'Electronics',
            price: 149.99,
            stock: 75
        }
    ];
    
    // Configure XLSX export
    const fileConfig = {
        format: 'xlsx',
        sheet_name: 'Products',
        include_headers: true,
        columns: ['sku', 'name', 'category', 'price', 'stock']
    };
    
    // Apply transformations before export
    const transformedProducts = products.map(product => ({
        sku: transform(product.sku, 'uppercase'),
        name: transform(product.name, 'title_case'),
        category: transform(product.category, 'uppercase'),
        price: product.price,
        stock: product.stock
    }));
    
    // Build XLSX
    const xlsxBuffer = buildXLSX(transformedProducts, fileConfig);
    
    // Save to file
    const outputPath = '/tmp/products_export.xlsx';
    await fs.writeFile(outputPath, xlsxBuffer);
    
    console.log(`✓ Exported ${products.length} products to ${outputPath}`);
    console.log(`  Sheet name: ${fileConfig.sheet_name}`);
    console.log(`  Columns: ${fileConfig.columns.join(', ')}`);
}

/**
 * Example 3: Export products to JSON
 */
async function exampleJSONExport() {
    console.log('\n=== Example 3: JSON Export ===\n');
    
    // Sample product data with nested attributes
    const products = [
        {
            sku: 'SKU001',
            name: 'Wireless Mouse',
            price: 29.99,
            attributes: {
                color: 'black',
                brand: 'TechCo',
                warranty: '2 years'
            },
            tags: ['wireless', 'ergonomic', 'usb']
        },
        {
            sku: 'SKU002',
            name: 'USB Cable',
            price: 9.99,
            attributes: {
                length: '6ft',
                type: 'USB-C',
                color: 'white'
            },
            tags: ['cable', 'usb-c', 'fast-charging']
        }
    ];
    
    // Configure JSON export
    const fileConfig = {
        format: 'json',
        pretty: true,
        indent: 2
    };
    
    // Apply transformations
    const transformedProducts = products.map(product => ({
        ...product,
        sku: transform(product.sku, 'uppercase'),
        name: transform(product.name, 'title_case'),
        tags: bulkApplyPipeRules(product.tags, 'uppercase')
    }));
    
    // Build JSON
    const jsonContent = buildJSON(transformedProducts, fileConfig);
    
    console.log('Generated JSON:');
    console.log(jsonContent);
    
    // Save to file
    const outputPath = '/tmp/products_export.json';
    await fs.writeFile(outputPath, jsonContent);
    
    console.log(`\n✓ Exported to ${outputPath}`);
}

/**
 * Example 4: Export products to XML
 */
async function exampleXMLExport() {
    console.log('\n=== Example 4: XML Export ===\n');
    
    // Sample product data
    const products = [
        {
            sku: 'SKU001',
            name: 'Wireless Mouse',
            price: 29.99,
            description: 'Ergonomic design & USB receiver'
        },
        {
            sku: 'SKU002',
            name: 'USB Cable',
            price: 9.99,
            description: 'USB-C cable - 6ft length'
        }
    ];
    
    // Configure XML export
    const fileConfig = {
        format: 'xml',
        root_element: 'products',
        item_element: 'product',
        pretty: true
    };
    
    // Apply transformations
    const transformedProducts = products.map(product => ({
        sku: transform(product.sku, 'uppercase'),
        name: transform(product.name, 'title_case'),
        price: product.price,
        description: transform(product.description, 'xml_escape')
    }));
    
    // Build XML
    const xmlContent = buildXML(transformedProducts, fileConfig);
    
    console.log('Generated XML:');
    console.log(xmlContent);
    
    // Save to file
    const outputPath = '/tmp/products_export.xml';
    await fs.writeFile(outputPath, xmlContent);
    
    console.log(`\n✓ Exported to ${outputPath}`);
}

/**
 * Example 5: Bulk export with complex transformations
 */
async function exampleBulkExportWithTransformations() {
    console.log('\n=== Example 5: Bulk Export with Transformations ===\n');
    
    // Large product dataset
    const products = [
        {
            sku: 'wm-001',
            name: '  wireless mouse  ',
            brand: 'TECHCO',
            price: '$29.99',
            sale_price: '$24.99',
            stock: '150',
            description: '<p>Great product!</p>',
            created_at: '2024-01-15T10:30:00Z'
        },
        {
            sku: 'uc-002',
            name: '  USB CABLE  ',
            brand: 'cabletech',
            price: '$9.99',
            sale_price: null,
            stock: '500',
            description: '<b>High quality</b>',
            created_at: '2024-01-16T14:20:00Z'
        },
        {
            sku: 'kb-003',
            name: '  mechanical keyboard  ',
            brand: 'KeyMaster',
            price: '$149.99',
            sale_price: '$129.99',
            stock: '75',
            description: 'Best keyboard ever!',
            created_at: '2024-01-17T09:15:00Z'
        }
    ];
    
    console.log(`Processing ${products.length} products...`);
    
    // Define transformation rules for each field
    const transformationRules = {
        sku: 'strip + uppercase',
        name: 'strip + title_case',
        brand: 'strip + title_case',
        price: 'clean_numeric_value + round_decimal|2',
        sale_price: 'clean_numeric_value + round_decimal|2',
        stock: 'clean_numeric_value',
        description: 'clean_html + strip',
        created_at: 'date_only'
    };
    
    // Apply transformations to all products
    const transformedProducts = products.map(product => {
        const transformed = {};
        
        for (const [field, value] of Object.entries(product)) {
            if (transformationRules[field]) {
                transformed[field] = transform(value, transformationRules[field]);
            } else {
                transformed[field] = value;
            }
        }
        
        // Calculate discount percentage if sale price exists
        if (transformed.sale_price && transformed.price) {
            const discount = ((transformed.price - transformed.sale_price) / transformed.price) * 100;
            transformed.discount_percent = transform(discount, 'round_decimal|0');
        } else {
            transformed.discount_percent = 0;
        }
        
        // Generate URL slug
        transformed.slug = transform(transformed.name, 'lowercase + replace| |-');
        
        return transformed;
    });
    
    console.log('\nTransformed products:');
    transformedProducts.forEach((product, i) => {
        console.log(`\n  Product ${i + 1}:`);
        for (const [key, value] of Object.entries(product)) {
            console.log(`    ${key}: ${value}`);
        }
    });
    
    // Export to CSV
    const fileConfig = {
        format: 'csv',
        delimiter: ',',
        include_headers: true,
        columns: ['sku', 'name', 'brand', 'price', 'sale_price', 'discount_percent', 'stock', 'slug']
    };
    
    const csvContent = buildCSV(transformedProducts, fileConfig);
    
    const outputPath = '/tmp/products_bulk_export.csv';
    await fs.writeFile(outputPath, csvContent);
    
    console.log(`\n✓ Exported ${transformedProducts.length} products to ${outputPath}`);
}

/**
 * Example 6: Channel-specific export (e.g., Amazon)
 */
async function exampleChannelSpecificExport() {
    console.log('\n=== Example 6: Channel-Specific Export ===\n');
    
    // Products with channel-specific transformations
    const products = [
        {
            internal_sku: 'WM-001',
            title: 'wireless mouse ergonomic design usb',
            bullet_1: 'Ergonomic design',
            bullet_2: 'USB receiver included',
            bullet_3: '2.4GHz wireless',
            price: 29.99,
            upc: '012345678905'
        },
        {
            internal_sku: 'UC-002',
            title: 'usb cable type c fast charging 6ft',
            bullet_1: 'USB-C connector',
            bullet_2: 'Fast charging support',
            bullet_3: '6 feet length',
            price: 9.99,
            upc: '012345678912'
        }
    ];
    
    console.log('Applying Amazon-specific transformations...');
    
    // Amazon-specific transformation rules
    const transformedProducts = products.map(product => {
        // SKU: uppercase
        const seller_sku = transform(product.internal_sku, 'uppercase');
        
        // Title: capitalize each word, max 200 chars
        let product_name = transform(product.title, 'title_case');
        product_name = product_name.length > 200 ? product_name.substring(0, 200) : product_name;
        
        // Bullets
        const bullet_point1 = transform(product.bullet_1, 'capitalize');
        const bullet_point2 = transform(product.bullet_2, 'capitalize');
        const bullet_point3 = transform(product.bullet_3, 'capitalize');
        
        // Price: format with 2 decimals
        const standard_price = transform(product.price, 'round_decimal|2');
        
        // UPC: clean and validate
        const product_id = transform(product.upc, 'clean_upc');
        
        return {
            seller_sku,
            product_name,
            product_id,
            product_id_type: 'UPC',
            bullet_point1,
            bullet_point2,
            bullet_point3,
            standard_price,
            quantity: 999,
            fulfillment_channel: 'DEFAULT'
        };
    });
    
    // Export to Amazon template format
    const fileConfig = {
        format: 'tsv',  // Amazon uses tab-delimited
        delimiter: '\t',
        include_headers: true,
        columns: [
            'seller_sku', 'product_name', 'product_id', 'product_id_type',
            'bullet_point1', 'bullet_point2', 'bullet_point3',
            'standard_price', 'quantity', 'fulfillment_channel'
        ]
    };
    
    // Build TSV
    const tsvContent = buildCSV(transformedProducts, fileConfig);  // CSV builder handles TSV too
    
    console.log('\nGenerated Amazon feed:');
    console.log(tsvContent);
    
    const outputPath = '/tmp/amazon_products_export.txt';
    await fs.writeFile(outputPath, tsvContent);
    
    console.log(`\n✓ Exported ${transformedProducts.length} products in Amazon format to ${outputPath}`);
}

/**
 * Main function - run all examples
 */
async function main() {
    console.log('='.repeat(60));
    console.log('JavaScript SDK Export Examples');
    console.log('='.repeat(60));
    
    await exampleCSVExport();
    await exampleXLSXExport();
    await exampleJSONExport();
    await exampleXMLExport();
    await exampleBulkExportWithTransformations();
    await exampleChannelSpecificExport();
    
    console.log('\n' + '='.repeat(60));
    console.log('All examples completed successfully!');
    console.log('='.repeat(60));
}

// Run if executed directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    exampleCSVExport,
    exampleXLSXExport,
    exampleJSONExport,
    exampleXMLExport,
    exampleBulkExportWithTransformations,
    exampleChannelSpecificExport
};
