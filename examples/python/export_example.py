"""
Python Export Example
Demonstrates exporting product data to CSV/XLSX/JSON/XML files
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import the SDK
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python-sdk"))

from saastify_edge.transformations import transform, bulk_apply_pipe_rules
from saastify_edge.export import build_csv, build_xlsx, build_json, build_xml


async def example_csv_export():
    """Example 1: Export products to CSV"""
    print("\n=== Example 1: CSV Export ===\n")
    
    # Sample product data
    products = [
        {
            'sku': 'SKU001',
            'name': 'Wireless Mouse',
            'price': 29.99,
            'description': 'Ergonomic wireless mouse with USB receiver'
        },
        {
            'sku': 'SKU002',
            'name': 'USB Cable',
            'price': 9.99,
            'description': 'High-quality USB-C cable'
        },
        {
            'sku': 'SKU003',
            'name': 'Mechanical Keyboard',
            'price': 149.99,
            'description': 'Cherry MX Blue switches'
        }
    ]
    
    # Configure CSV export
    file_config = {
        'format': 'csv',
        'delimiter': ',',
        'include_headers': True,
        'columns': ['sku', 'name', 'price', 'description']
    }
    
    # Apply transformations before export
    transformed_products = []
    for product in products:
        transformed = product.copy()
        # Uppercase SKU
        transformed['sku'] = transform(product['sku'], 'uppercase')
        # Title case name
        transformed['name'] = transform(product['name'], 'title_case')
        # Format price with 2 decimals
        transformed['price'] = transform(product['price'], 'round_decimal|2')
        transformed_products.append(transformed)
    
    # Build CSV
    csv_content = build_csv(transformed_products, file_config)
    
    print("Generated CSV:")
    print(csv_content)
    
    # Save to file
    output_path = '/tmp/products_export.csv'
    with open(output_path, 'w') as f:
        f.write(csv_content)
    
    print(f"\n✓ Exported to {output_path}")


async def example_xlsx_export():
    """Example 2: Export products to Excel (XLSX)"""
    print("\n=== Example 2: XLSX Export ===\n")
    
    # Sample product data
    products = [
        {
            'sku': 'SKU001',
            'name': 'Wireless Mouse',
            'category': 'Electronics',
            'price': 29.99,
            'stock': 150
        },
        {
            'sku': 'SKU002',
            'name': 'USB Cable',
            'category': 'Accessories',
            'price': 9.99,
            'stock': 500
        },
        {
            'sku': 'SKU003',
            'name': 'Mechanical Keyboard',
            'category': 'Electronics',
            'price': 149.99,
            'stock': 75
        }
    ]
    
    # Configure XLSX export
    file_config = {
        'format': 'xlsx',
        'sheet_name': 'Products',
        'include_headers': True,
        'columns': ['sku', 'name', 'category', 'price', 'stock']
    }
    
    # Apply transformations before export
    transformed_products = []
    for product in products:
        transformed = product.copy()
        transformed['sku'] = transform(product['sku'], 'uppercase')
        transformed['name'] = transform(product['name'], 'title_case')
        transformed['category'] = transform(product['category'], 'uppercase')
        transformed_products.append(transformed)
    
    # Build XLSX
    xlsx_bytes = build_xlsx(transformed_products, file_config)
    
    # Save to file
    output_path = '/tmp/products_export.xlsx'
    with open(output_path, 'wb') as f:
        f.write(xlsx_bytes)
    
    print(f"✓ Exported {len(products)} products to {output_path}")
    print(f"  Sheet name: {file_config['sheet_name']}")
    print(f"  Columns: {', '.join(file_config['columns'])}")


async def example_json_export():
    """Example 3: Export products to JSON"""
    print("\n=== Example 3: JSON Export ===\n")
    
    # Sample product data with nested attributes
    products = [
        {
            'sku': 'SKU001',
            'name': 'Wireless Mouse',
            'price': 29.99,
            'attributes': {
                'color': 'black',
                'brand': 'TechCo',
                'warranty': '2 years'
            },
            'tags': ['wireless', 'ergonomic', 'usb']
        },
        {
            'sku': 'SKU002',
            'name': 'USB Cable',
            'price': 9.99,
            'attributes': {
                'length': '6ft',
                'type': 'USB-C',
                'color': 'white'
            },
            'tags': ['cable', 'usb-c', 'fast-charging']
        }
    ]
    
    # Configure JSON export
    file_config = {
        'format': 'json',
        'pretty': True,
        'indent': 2
    }
    
    # Apply transformations
    transformed_products = []
    for product in products:
        transformed = product.copy()
        # Uppercase SKU
        transformed['sku'] = transform(product['sku'], 'uppercase')
        # Title case name
        transformed['name'] = transform(product['name'], 'title_case')
        # Transform tags to uppercase
        transformed['tags'] = bulk_apply_pipe_rules(product['tags'], 'uppercase')
        transformed_products.append(transformed)
    
    # Build JSON
    json_content = build_json(transformed_products, file_config)
    
    print("Generated JSON:")
    print(json_content)
    
    # Save to file
    output_path = '/tmp/products_export.json'
    with open(output_path, 'w') as f:
        f.write(json_content)
    
    print(f"\n✓ Exported to {output_path}")


async def example_xml_export():
    """Example 4: Export products to XML"""
    print("\n=== Example 4: XML Export ===\n")
    
    # Sample product data
    products = [
        {
            'sku': 'SKU001',
            'name': 'Wireless Mouse',
            'price': 29.99,
            'description': 'Ergonomic design & USB receiver'
        },
        {
            'sku': 'SKU002',
            'name': 'USB Cable',
            'price': 9.99,
            'description': 'USB-C cable - 6ft length'
        }
    ]
    
    # Configure XML export
    file_config = {
        'format': 'xml',
        'root_element': 'products',
        'item_element': 'product',
        'pretty': True
    }
    
    # Apply transformations
    transformed_products = []
    for product in products:
        transformed = product.copy()
        # Uppercase SKU
        transformed['sku'] = transform(product['sku'], 'uppercase')
        # Title case name
        transformed['name'] = transform(product['name'], 'title_case')
        # Clean description for XML
        transformed['description'] = transform(product['description'], 'xml_escape')
        transformed_products.append(transformed)
    
    # Build XML
    xml_content = build_xml(transformed_products, file_config)
    
    print("Generated XML:")
    print(xml_content)
    
    # Save to file
    output_path = '/tmp/products_export.xml'
    with open(output_path, 'w') as f:
        f.write(xml_content)
    
    print(f"\n✓ Exported to {output_path}")


async def example_bulk_export_with_transformations():
    """Example 5: Bulk export with complex transformations"""
    print("\n=== Example 5: Bulk Export with Transformations ===\n")
    
    # Large product dataset
    products = [
        {
            'sku': 'wm-001',
            'name': '  wireless mouse  ',
            'brand': 'TECHCO',
            'price': '$29.99',
            'sale_price': '$24.99',
            'stock': '150',
            'description': '<p>Great product!</p>',
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'sku': 'uc-002',
            'name': '  USB CABLE  ',
            'brand': 'cabletech',
            'price': '$9.99',
            'sale_price': None,
            'stock': '500',
            'description': '<b>High quality</b>',
            'created_at': '2024-01-16T14:20:00Z'
        },
        {
            'sku': 'kb-003',
            'name': '  mechanical keyboard  ',
            'brand': 'KeyMaster',
            'price': '$149.99',
            'sale_price': '$129.99',
            'stock': '75',
            'description': 'Best keyboard ever!',
            'created_at': '2024-01-17T09:15:00Z'
        }
    ]
    
    print(f"Processing {len(products)} products...")
    
    # Define transformation rules for each field
    transformation_rules = {
        'sku': 'strip + uppercase',
        'name': 'strip + title_case',
        'brand': 'strip + title_case',
        'price': 'clean_numeric_value + round_decimal|2',
        'sale_price': 'clean_numeric_value + round_decimal|2',
        'stock': 'clean_numeric_value',
        'description': 'clean_html + strip',
        'created_at': 'date_only'
    }
    
    # Apply transformations to all products
    transformed_products = []
    for product in products:
        transformed = {}
        for field, value in product.items():
            if field in transformation_rules:
                rule = transformation_rules[field]
                transformed[field] = transform(value, rule)
            else:
                transformed[field] = value
        
        # Calculate discount percentage if sale price exists
        if transformed.get('sale_price') and transformed.get('price'):
            discount = ((transformed['price'] - transformed['sale_price']) / transformed['price']) * 100
            transformed['discount_percent'] = transform(discount, 'round_decimal|0')
        else:
            transformed['discount_percent'] = 0
        
        # Generate URL slug
        transformed['slug'] = transform(transformed['name'], 'lowercase + replace| |-')
        
        transformed_products.append(transformed)
    
    print("\nTransformed products:")
    for i, product in enumerate(transformed_products, 1):
        print(f"\n  Product {i}:")
        for key, value in product.items():
            print(f"    {key}: {value}")
    
    # Export to CSV
    file_config = {
        'format': 'csv',
        'delimiter': ',',
        'include_headers': True,
        'columns': ['sku', 'name', 'brand', 'price', 'sale_price', 'discount_percent', 'stock', 'slug']
    }
    
    csv_content = build_csv(transformed_products, file_config)
    
    output_path = '/tmp/products_bulk_export.csv'
    with open(output_path, 'w') as f:
        f.write(csv_content)
    
    print(f"\n✓ Exported {len(transformed_products)} products to {output_path}")


async def example_channel_specific_export():
    """Example 6: Channel-specific export (e.g., Amazon)"""
    print("\n=== Example 6: Channel-Specific Export ===\n")
    
    # Products with channel-specific transformations
    products = [
        {
            'internal_sku': 'WM-001',
            'title': 'wireless mouse ergonomic design usb',
            'bullet_1': 'Ergonomic design',
            'bullet_2': 'USB receiver included',
            'bullet_3': '2.4GHz wireless',
            'price': 29.99,
            'upc': '012345678905'
        },
        {
            'internal_sku': 'UC-002',
            'title': 'usb cable type c fast charging 6ft',
            'bullet_1': 'USB-C connector',
            'bullet_2': 'Fast charging support',
            'bullet_3': '6 feet length',
            'price': 9.99,
            'upc': '012345678912'
        }
    ]
    
    print("Applying Amazon-specific transformations...")
    
    # Amazon-specific transformation rules
    transformed_products = []
    for product in products:
        transformed = {}
        
        # SKU: uppercase
        transformed['seller_sku'] = transform(product['internal_sku'], 'uppercase')
        
        # Title: capitalize each word, max 200 chars
        title = transform(product['title'], 'title_case')
        transformed['product_name'] = title[:200] if len(title) > 200 else title
        
        # Bullets: combine into description
        bullets = [product['bullet_1'], product['bullet_2'], product['bullet_3']]
        transformed['bullet_point1'] = transform(bullets[0], 'capitalize')
        transformed['bullet_point2'] = transform(bullets[1], 'capitalize')
        transformed['bullet_point3'] = transform(bullets[2], 'capitalize')
        
        # Price: format with 2 decimals
        transformed['standard_price'] = transform(product['price'], 'round_decimal|2')
        
        # UPC: clean and validate
        transformed['product_id'] = transform(product['upc'], 'clean_upc')
        transformed['product_id_type'] = 'UPC'
        
        # Quantity: required field
        transformed['quantity'] = 999
        
        # Fulfillment: FBA or FBM
        transformed['fulfillment_channel'] = 'DEFAULT'
        
        transformed_products.append(transformed)
    
    # Export to Amazon template format
    file_config = {
        'format': 'tsv',  # Amazon uses tab-delimited
        'delimiter': '\t',
        'include_headers': True,
        'columns': [
            'seller_sku', 'product_name', 'product_id', 'product_id_type',
            'bullet_point1', 'bullet_point2', 'bullet_point3',
            'standard_price', 'quantity', 'fulfillment_channel'
        ]
    }
    
    # Build TSV
    tsv_content = build_csv(transformed_products, file_config)  # CSV builder handles TSV too
    
    print("\nGenerated Amazon feed:")
    print(tsv_content)
    
    output_path = '/tmp/amazon_products_export.txt'
    with open(output_path, 'w') as f:
        f.write(tsv_content)
    
    print(f"\n✓ Exported {len(transformed_products)} products in Amazon format to {output_path}")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Python SDK Export Examples")
    print("=" * 60)
    
    await example_csv_export()
    await example_xlsx_export()
    await example_json_export()
    await example_xml_export()
    await example_bulk_export_with_transformations()
    await example_channel_specific_export()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
