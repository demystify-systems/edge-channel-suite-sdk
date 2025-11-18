"""
Test parsers and validation engine
Run with: python3 test_parsers_validation.py
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from saastify_edge.core.parsers import get_parser, detect_file_type
from saastify_edge.validation import validate_row, validate_field
from saastify_edge.transformations import apply_transformations


async def test_csv_parser():
    """Test CSV parsing"""
    print("Testing CSV parser...")
    
    csv_file = "test_data/sample_products.csv"
    parser = get_parser(csv_file)
    
    rows = []
    async for row in parser.parse(csv_file):
        rows.append(row)
    
    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"
    assert rows[0]["data"]["SKU"] == "SKU001"
    assert rows[0]["data"]["Name"] == "Blue T-Shirt"
    assert rows[0]["data"]["Price"] == "19.99"
    
    print(f"✓ Parsed {len(rows)} rows from CSV")
    print(f"  First row: {rows[0]['data']}")
    return rows


def test_validation():
    """Test validation engine"""
    print("\nTesting validation engine...")
    
    # Test required rule
    errors = validate_field(
        "name",
        None,
        [{"rule": "required"}]
    )
    assert len(errors) == 1
    assert errors[0]["rule"] == "required"
    print("✓ Required validation works")
    
    # Test regex rule
    errors = validate_field(
        "sku",
        "ABC123",
        [{"rule": "regex", "args": {"pattern": "^[A-Z]{3}\\d{3}$"}}]
    )
    assert len(errors) == 0
    print("✓ Regex validation works")
    
    # Test enum rule
    errors = validate_field(
        "category",
        "Books",
        [{"rule": "enum", "args": {"values": ["Apparel", "Accessories", "Footwear"]}}]
    )
    assert len(errors) == 1
    print("✓ Enum validation works")
    
    # Test numeric_range
    errors = validate_field(
        "price",
        15.00,
        [{"rule": "numeric_range", "args": {"min": 10, "max": 100}}]
    )
    assert len(errors) == 0
    print("✓ Numeric range validation works")
    
    # Test row validation
    row_data = {
        "sku": "SKU001",
        "name": "Product",
        "price": 25.00,
        "category": "Apparel"
    }
    
    validations = {
        "sku": [{"rule": "required"}],
        "name": [{"rule": "required"}, {"rule": "min_length", "args": {"value": 3}}],
        "price": [{"rule": "numeric_range", "args": {"min": 0, "max": 1000}}],
        "category": [{"rule": "enum", "args": {"values": ["Apparel", "Accessories", "Footwear"]}}]
    }
    
    is_valid, errors, error_count = validate_row(row_data, validations)
    assert is_valid
    assert error_count == 0
    print("✓ Row validation works")


async def test_integrated_pipeline():
    """Test integrated transformation + validation"""
    print("\nTesting integrated pipeline...")
    
    # Simulate a row from CSV
    raw_row = {
        "SKU": " sku001 ",
        "Name": "  BLUE T-SHIRT  ",
        "Price": "$19.99",
        "Category": "apparel"
    }
    
    # Define transformations
    transformations_map = {
        "SKU": [
            {"name": "strip"},
            {"name": "uppercase"}
        ],
        "Name": [
            {"name": "strip"},
            {"name": "title_case"}
        ],
        "Price": [
            {"name": "clean_numeric_value"}
        ],
        "Category": [
            {"name": "strip"},
            {"name": "lowercase"}
        ]
    }
    
    # Apply transformations
    transformed_row = {}
    for field, value in raw_row.items():
        if field in transformations_map:
            transformed_value, rejected = apply_transformations(
                value,
                transformations_map[field]
            )
            if not rejected:
                transformed_row[field] = transformed_value
        else:
            transformed_row[field] = value
    
    print(f"  Raw row: {raw_row}")
    print(f"  Transformed: {transformed_row}")
    
    # Validate transformed data
    validations = {
        "SKU": [
            {"rule": "required"},
            {"rule": "regex", "args": {"pattern": "^SKU\\d{3}$"}}
        ],
        "Name": [
            {"rule": "required"},
            {"rule": "min_length", "args": {"value": 3}}
        ],
        "Price": [
            {"rule": "numeric_range", "args": {"min": 0, "max": 1000}}
        ],
        "Category": [
            {"rule": "enum", "args": {"values": ["apparel", "accessories", "footwear"]}}
        ]
    }
    
    is_valid, errors, error_count = validate_row(transformed_row, validations)
    
    print(f"  Valid: {is_valid}")
    print(f"  Errors: {errors}")
    
    assert is_valid, f"Expected valid row but got errors: {errors}"
    print("✓ Integrated pipeline works")


def test_file_type_detection():
    """Test file type detection"""
    print("\nTesting file type detection...")
    
    assert detect_file_type("data.csv") == "CSV"
    assert detect_file_type("data.tsv") == "TSV"
    assert detect_file_type("data.xlsx") == "XLSX"
    assert detect_file_type("data.json") == "JSON"
    assert detect_file_type("data.xml") == "XML"
    
    print("✓ File type detection works")


async def main():
    try:
        # Run tests
        test_file_type_detection()
        await test_csv_parser()
        test_validation()
        await test_integrated_pipeline()
        
        print("\n" + "="*50)
        print("✅ All parser and validation tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
