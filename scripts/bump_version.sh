#!/bin/bash

# Version Bump Script
# Updates version in both Python and JavaScript SDKs

VERSION_TYPE=$1

if [ -z "$VERSION_TYPE" ]; then
    echo "Usage: ./scripts/bump_version.sh [major|minor|patch]"
    echo ""
    echo "Examples:"
    echo "  ./scripts/bump_version.sh patch   # 1.0.0 -> 1.0.1"
    echo "  ./scripts/bump_version.sh minor   # 1.0.0 -> 1.1.0"
    echo "  ./scripts/bump_version.sh major   # 1.0.0 -> 2.0.0"
    exit 1
fi

# Get repository root
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Python SDK
cd "$REPO_ROOT/python-sdk"
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📦 Current Python version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

case $VERSION_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "❌ Invalid version type: $VERSION_TYPE"
        echo "   Must be one of: major, minor, patch"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "🎯 New version: $NEW_VERSION"
echo ""

# Update Python SDK
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
else
    # Linux
    sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
fi
echo "✓ Updated python-sdk/pyproject.toml"

# Update JavaScript SDK
cd "$REPO_ROOT/js-sdk"
npm version $NEW_VERSION --no-git-tag-version > /dev/null 2>&1
echo "✓ Updated js-sdk/package.json"

cd "$REPO_ROOT"
echo ""
echo "✅ Version bumped to $NEW_VERSION in both SDKs"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Commit: git commit -am \"Bump version to $NEW_VERSION\""
echo "   3. Tag: git tag v$NEW_VERSION"
echo "   4. Push: git push && git push --tags"
echo ""
echo "Or use automated release:"
echo "   ./scripts/release.sh $NEW_VERSION"
