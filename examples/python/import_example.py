"""
Python Import Example
Demonstrates importing product data from CSV/XLSX/JSON/XML files
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import the SDK
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python-sdk"))

from saastify_edge.transformations import transform, bulk_apply_pipe_rules
from saastify_edge.validation import validate_row
from saastify_edge.core.parsers import get_parser


async def example_basic_import():
    """Example 1: Basic CSV import with transformations"""
    print("\n=== Example 1: Basic CSV Import ===\n")
    
    # Sample CSV data (in real use, this would be a file)
    csv_data = """SKU,Product Name,Price,Description
    SKU001,  wireless mouse  ,$29.99,"<p>Great mouse</p>"
    SKU002,  USB CABLE  ,$9.99,"<b>High quality</b>"
    SKU003,  keyboard  ,$49.99,"Mechanical keyboard"
    """
    
    # Write sample data to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_file = f.name
    
    # Parse CSV file
    parser = get_parser(temp_file)
    
    async for row in parser.parse(temp_file):
        print(f"Row {row['file_row_number']}:")
        print(f"  Raw data: {row['data']}")
        
        # Apply transformations
        transformed = {}
        transformed['sku'] = transform(row['data']['SKU'], 'strip + uppercase')
        transformed['name'] = transform(row['data']['Product Name'], 'strip + title_case')
        transformed['price'] = transform(row['data']['Price'], 'clean_numeric_value + round_decimal|2')
        transformed['description'] = transform(row['data']['Description'], 'clean_html + strip')
        
        print(f"  Transformed: {transformed}")
        
        # Validate
        validations = {
            'sku': [{'rule': 'required'}],
            'name': [{'rule': 'required'}, {'rule': 'min_length', 'args': {'value': 3}}],
            'price': [{'rule': 'numeric_range', 'args': {'min': 0, 'max': 10000}}]
        }
        
        is_valid, errors, error_count = validate_row(transformed, validations)
        print(f"  Valid: {is_valid}, Errors: {error_count}")
        if errors:
            print(f"  Validation errors: {errors}")
        print()
    
    # Cleanup
    import os
    os.unlink(temp_file)


async def example_bulk_transformations():
    """Example 2: Bulk transformations with DSL"""
    print("\n=== Example 2: Bulk Transformations ===\n")
    
    # Sample product data
    product_names = [
        "  wireless mouse  ",
        "  USB CABLE  ",
        "  mechanical keyboard  ",
        "  hdmi cable 4k  "
    ]
    
    prices = ["$29.99", "$9.99", "$149.99", "$19.99"]
    skus = ["WM-001", "UC-002", "KB-003", "HC-004"]
    
    # Transform product names
    print("Transforming product names:")
    cleaned_names = bulk_apply_pipe_rules(
        product_names,
        "strip + title_case"
    )
    for original, cleaned in zip(product_names, cleaned_names):
        print(f"  '{original}' → '{cleaned}'")
    
    # Transform prices
    print("\nTransforming prices:")
    numeric_prices = bulk_apply_pipe_rules(
        prices,
        "clean_numeric_value + round_decimal|2"
    )
    for original, cleaned in zip(prices, numeric_prices):
        print(f"  '{original}' → {cleaned}")
    
    # Generate slugs for URLs
    print("\nGenerating URL slugs:")
    slugs = bulk_apply_pipe_rules(
        cleaned_names,
        "lowercase + replace| |-"
    )
    for name, slug in zip(cleaned_names, slugs):
        print(f"  '{name}' → '{slug}'")
    
    # Create full product objects
    print("\nFull product objects:")
    for i in range(len(skus)):
        product = {
            'sku': skus[i],
            'name': cleaned_names[i],
            'price': numeric_prices[i],
            'slug': slugs[i]
        }
        print(f"  {product}")


async def example_advanced_transformations():
    """Example 3: Advanced transformations with multiple operations"""
    print("\n=== Example 3: Advanced Transformations ===\n")
    
    # Date transformations
    print("Date transformations:")
    from datetime import datetime
    today = datetime.now()
    
    formatted_date = transform(today, "format_date|%Y-%m-%d")
    print(f"  Formatted date: {formatted_date}")
    
    future_date = transform(today, "add_days|30 + format_date|%Y-%m-%d")
    print(f"  30 days from now: {future_date}")
    
    # String manipulations
    print("\nString manipulations:")
    brand = "ACME Corp"
    product = "Wireless Mouse"
    
    combined = transform(f"{brand} {product}", "uppercase + replace| |_")
    print(f"  Combined: '{combined}'")
    
    # Numeric operations
    print("\nNumeric operations:")
    base_price = 100.00
    
    discounted = transform(base_price, "multiplication|0.8 + round_decimal|2")
    print(f"  20% discount: ${discounted}")
    
    with_tax = transform(base_price, "multiplication|1.08 + round_decimal|2")
    print(f"  With 8% tax: ${with_tax}")
    
    # Conditional transformations
    print("\nConditional transformations:")
    empty_description = ""
    description = transform(empty_description, "if_empty|No description available")
    print(f"  Empty description: '{description}'")


async def example_validation():
    """Example 4: Comprehensive validation"""
    print("\n=== Example 4: Validation Examples ===\n")
    
    # Test data
    test_products = [
        {
            'sku': 'SKU001',
            'name': 'Wireless Mouse',
            'price': 29.99,
            'email': 'contact@example.com',
            'website': 'https://example.com',
            'phone': '+1-555-123-4567'
        },
        {
            'sku': '',  # Invalid: required
            'name': 'KB',  # Invalid: too short
            'price': 15000,  # Invalid: too expensive
            'email': 'invalid-email',  # Invalid format
            'website': 'not-a-url',  # Invalid format
            'phone': '123'  # Invalid: too short
        }
    ]
    
    # Validation rules
    validations = {
        'sku': [
            {'rule': 'required'}
        ],
        'name': [
            {'rule': 'required'},
            {'rule': 'min_length', 'args': {'value': 3}},
            {'rule': 'max_length', 'args': {'value': 100}}
        ],
        'price': [
            {'rule': 'required'},
            {'rule': 'numeric_range', 'args': {'min': 0, 'max': 10000}}
        ],
        'email': [
            {'rule': 'email'}
        ],
        'website': [
            {'rule': 'url'}
        ],
        'phone': [
            {'rule': 'phone'}
        ]
    }
    
    # Validate each product
    for i, product in enumerate(test_products, 1):
        print(f"Product {i}:")
        print(f"  Data: {product}")
        
        is_valid, errors, error_count = validate_row(product, validations)
        
        print(f"  Valid: {is_valid}")
        if errors:
            print(f"  Errors ({error_count}):")
            for field, field_errors in errors.items():
                for error in field_errors:
                    print(f"    - {field}: {error['message']}")
        print()


async def example_file_formats():
    """Example 5: Working with different file formats"""
    print("\n=== Example 5: Multiple File Formats ===\n")
    
    import tempfile
    import json
    
    # Sample data
    products = [
        {'sku': 'SKU001', 'name': 'Product 1', 'price': 29.99},
        {'sku': 'SKU002', 'name': 'Product 2', 'price': 49.99},
    ]
    
    # JSON example
    print("JSON format:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(products, f)
        json_file = f.name
    
    parser = get_parser(json_file)
    row_count = 0
    async for row in parser.parse(json_file):
        row_count += 1
        print(f"  Row {row_count}: {row['data']}")
    
    import os
    os.unlink(json_file)
    
    print("\n✓ CSV, TSV, XLSX, JSON, and XML formats all supported!")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Python SDK Import Examples")
    print("=" * 60)
    
    await example_basic_import()
    await example_bulk_transformations()
    await example_advanced_transformations()
    await example_validation()
    await example_file_formats()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
