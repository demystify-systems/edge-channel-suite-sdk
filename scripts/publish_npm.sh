#!/bin/bash

# JavaScript SDK Publishing Script

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT/js-sdk"

echo "📦 Publishing JavaScript SDK to npm"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

# Check if logged in
echo "🔑 Checking npm login..."
npm whoami > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Not logged in to npm"
    echo "   Run: npm login"
    exit 1
fi
echo "✓ Logged in as: $(npm whoami)"

# Clean and install
echo ""
echo "🧹 Cleaning and installing dependencies..."
rm -rf dist/ node_modules/
npm install > /dev/null 2>&1
echo "✓ Dependencies installed"

# Build
echo ""
echo "🔨 Building package..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✓ Build complete"

# Type check
echo ""
echo "🔍 Running type check..."
npm run typecheck
if [ $? -ne 0 ]; then
    echo "⚠️  Type check failed"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Type check passed"
fi

# Dry run
echo ""
echo "📋 Dry run (showing what will be published)..."
npm publish --dry-run
echo ""

# Ask for confirmation
read -p "Publish to npm? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Publish cancelled"
    exit 1
fi

# Publish
echo ""
echo "⬆️  Publishing to npm..."
npm publish --access public

if [ $? -eq 0 ]; then
    VERSION=$(node -p "require('./package.json').version")
    PACKAGE_NAME=$(node -p "require('./package.json').name")
    echo ""
    echo "✅ Successfully published to npm!"
    echo "   View at: https://www.npmjs.com/package/$PACKAGE_NAME/v/$VERSION"
else
    echo "❌ Publish failed"
    exit 1
fi
