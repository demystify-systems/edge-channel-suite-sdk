"""
Basic tests for transformation engine
Run with: python3 test_transformations.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from saastify_edge.transformations import bulk_apply_pipe_rules, apply_transformations


def test_basic_operations():
    """Test basic transformation operations"""
    print("Testing basic operations...")
    
    # Uppercase
    result = bulk_apply_pipe_rules(["hello", "world"], "uppercase")
    assert result == ["HELLO", "WORLD"], f"Expected ['HELLO', 'WORLD'], got {result}"
    print("✓ uppercase works")
    
    # Lowercase
    result = bulk_apply_pipe_rules(["HELLO", "WORLD"], "lowercase")
    assert result == ["hello", "world"], f"Expected ['hello', 'world'], got {result}"
    print("✓ lowercase works")
    
    # Strip
    result = bulk_apply_pipe_rules(["  test  "], "strip")
    assert result == ["test"], f"Expected ['test'], got {result}"
    print("✓ strip works")
    
    # Chain operations
    result = bulk_apply_pipe_rules(["  hello world  "], "uppercase + strip")
    assert result == ["HELLO WORLD"], f"Expected ['HELLO WORLD'], got {result}"
    print("✓ chaining works")


def test_parameterized_operations():
    """Test operations with parameters"""
    print("\nTesting parameterized operations...")
    
    # Replace
    result = bulk_apply_pipe_rules(["hello-world"], "replace|-|_")
    assert result == ["hello_world"], f"Expected ['hello_world'], got {result}"
    print("✓ replace works")
    
    # Split
    result = bulk_apply_pipe_rules(["a,b,c"], "split|,")
    assert result == [["a", "b", "c"]], f"Expected [['a', 'b', 'c']], got {result}"
    print("✓ split works")
    
    # Join
    result = bulk_apply_pipe_rules([["a", "b", "c"]], "join|,")
    assert result == ["a,b,c"], f"Expected ['a,b,c'], got {result}"
    print("✓ join works")


def test_numeric_operations():
    """Test numeric operations"""
    print("\nTesting numeric operations...")
    
    # Addition
    result = bulk_apply_pipe_rules([10], "addition|5")
    assert result == [15], f"Expected [15], got {result}"
    print("✓ addition works")
    
    # Multiplication
    result = bulk_apply_pipe_rules([10], "multiplication|2")
    assert result == [20], f"Expected [20], got {result}"
    print("✓ multiplication works")
    
    # Clean numeric value
    result = bulk_apply_pipe_rules(["$1,234.56"], "clean_numeric_value")
    assert result == [1234.56], f"Expected [1234.56], got {result}"
    print("✓ clean_numeric_value works")


def test_complex_pipeline():
    """Test complex transformation pipeline"""
    print("\nTesting complex pipeline...")
    
    # Transform: "  HELLO WORLD  " → "hello_world"
    result = bulk_apply_pipe_rules(
        ["  HELLO WORLD  "],
        "strip + lowercase + replace| |_"
    )
    assert result == ["hello_world"], f"Expected ['hello_world'], got {result}"
    print("✓ complex pipeline works")


def test_structured_pipeline():
    """Test structured transformation steps"""
    print("\nTesting structured pipeline...")
    
    steps = [
        {"name": "strip"},
        {"name": "uppercase"},
        {"name": "replace", "params": {"old": " ", "new": "-"}}
    ]
    
    result, rejected = apply_transformations("  hello world  ", steps)
    assert result == "HELLO-WORLD", f"Expected 'HELLO-WORLD', got {result}"
    assert not rejected, "Row should not be rejected"
    print("✓ structured pipeline works")


def test_broadcasting():
    """Test broadcasting rules"""
    print("\nTesting broadcasting...")
    
    # Single rule, multiple values
    result = bulk_apply_pipe_rules(["hello", "world", "test"], "uppercase")
    assert result == ["HELLO", "WORLD", "TEST"]
    print("✓ single rule → multiple values")
    
    # Multiple values, single rule in list
    result = bulk_apply_pipe_rules(["hello", "world"], ["uppercase"])
    assert result == ["HELLO", "WORLD"]
    print("✓ multiple values → single rule in list")


if __name__ == "__main__":
    try:
        test_basic_operations()
        test_parameterized_operations()
        test_numeric_operations()
        test_complex_pipeline()
        test_structured_pipeline()
        test_broadcasting()
        
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
