#!/bin/bash

# Python SDK Publishing Script

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT/python-sdk"

echo "🐍 Publishing Python SDK to PyPI"
echo ""

# Check if build and twine are installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "📦 Installing build tools..."
pip install --upgrade build twine > /dev/null 2>&1
echo "✓ Build tools installed"

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info
echo "✓ Cleaned"

# Build package
echo ""
echo "🔨 Building package..."
python3 -m build
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✓ Build complete"

# Check package
echo ""
echo "🔍 Checking package..."
twine check dist/*
if [ $? -ne 0 ]; then
    echo "❌ Package check failed"
    exit 1
fi
echo "✓ Package is valid"

# Show package info
echo ""
echo "📋 Package information:"
ls -lh dist/
echo ""

# Ask for confirmation
read -p "Upload to PyPI? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upload cancelled"
    exit 1
fi

# Upload to PyPI
echo ""
echo "⬆️  Uploading to PyPI..."
twine upload dist/*

if [ $? -eq 0 ]; then
    VERSION=$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo ""
    echo "✅ Successfully published to PyPI!"
    echo "   View at: https://pypi.org/project/saastify-edge-sdk/$VERSION/"
else
    echo "❌ Upload failed"
    exit 1
fi
