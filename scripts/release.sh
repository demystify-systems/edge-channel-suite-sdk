#!/bin/bash

# Automated Release Script
# Bumps version, commits, tags, and pushes

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo ""
    echo "Examples:"
    echo "  ./scripts/release.sh 1.0.1"
    echo "  ./scripts/release.sh 1.1.0"
    echo "  ./scripts/release.sh 2.0.0"
    exit 1
fi

# Get repository root
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT"

echo "🚀 Starting release process for version $VERSION"
echo ""

# Check if working directory is clean
if [[ -n $(git status -s) ]]; then
    echo "❌ Working directory is not clean. Please commit or stash changes first."
    git status -s
    exit 1
fi

# Update Python SDK version
echo "📝 Updating Python SDK..."
cd "$REPO_ROOT/python-sdk"
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml
else
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml
fi
echo "✓ Updated python-sdk/pyproject.toml: $CURRENT_VERSION → $VERSION"

# Update JavaScript SDK version
echo "📝 Updating JavaScript SDK..."
cd "$REPO_ROOT/js-sdk"
npm version $VERSION --no-git-tag-version > /dev/null 2>&1
echo "✓ Updated js-sdk/package.json: $CURRENT_VERSION → $VERSION"

# Commit changes
cd "$REPO_ROOT"
echo ""
echo "📦 Committing changes..."
git add python-sdk/pyproject.toml js-sdk/package.json
git commit -m "Release v$VERSION

- Bump version to $VERSION in both SDKs
- Ready for publishing to PyPI and npm"
echo "✓ Changes committed"

# Create tag
echo ""
echo "🏷️  Creating tag..."
git tag -a "v$VERSION" -m "Release version $VERSION"
echo "✓ Tag v$VERSION created"

# Push changes
echo ""
echo "⬆️  Pushing to remote..."
git push origin main
git push origin "v$VERSION"
echo "✓ Changes and tags pushed"

echo ""
echo "✅ Release v$VERSION complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Publish Python SDK: cd python-sdk && ./scripts/publish_python.sh"
echo "   2. Publish JavaScript SDK: cd js-sdk && ./scripts/publish_npm.sh"
echo ""
echo "   Or wait for GitHub Actions to automatically publish"
