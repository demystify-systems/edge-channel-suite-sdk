# Publishing Guide

This guide covers how to publish both the Python SDK (to PyPI) and JavaScript SDK (to npm).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Python SDK Publishing (PyPI)](#python-sdk-publishing-pypi)
3. [JavaScript SDK Publishing (npm)](#javascript-sdk-publishing-npm)
4. [Version Management](#version-management)
5. [CI/CD Automation](#cicd-automation)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### For Python SDK (PyPI)

1. **Install build tools:**
   ```bash
   pip install --upgrade build twine
   ```

2. **Create PyPI account:**
   - Sign up at https://pypi.org/account/register/
   - Verify your email
   - Enable 2FA (recommended)

3. **Create API token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope "Entire account" or specific to `saastify-edge-sdk`
   - Save the token securely (it starts with `pypi-`)

4. **Configure credentials:**
   ```bash
   # Create/edit ~/.pypirc
   cat > ~/.pypirc << EOF
   [pypi]
   username = __token__
   password = pypi-YOUR_TOKEN_HERE
   EOF
   chmod 600 ~/.pypirc
   ```

### For JavaScript SDK (npm)

1. **Install Node.js:**
   - Version 14 or higher
   - Download from https://nodejs.org/

2. **Create npm account:**
   - Sign up at https://www.npmjs.com/signup
   - Verify your email

3. **Login to npm:**
   ```bash
   npm login
   ```
   
   Or use authentication token:
   ```bash
   npm config set //registry.npmjs.org/:_authToken YOUR_TOKEN_HERE
   ```

4. **Request organization access (if using @saastify scope):**
   - Contact npm to create `@saastify` organization
   - Or publish under your personal scope initially

---

## Python SDK Publishing (PyPI)

### Step 1: Prepare the Release

```bash
cd python-sdk

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Update version in pyproject.toml
# Edit version = "1.0.1" or use script (see Version Management section)
```

### Step 2: Build the Package

```bash
# Build source distribution and wheel
python -m build

# This creates:
# - dist/saastify_edge_sdk-1.0.0.tar.gz
# - dist/saastify_edge_sdk-1.0.0-py3-none-any.whl
```

### Step 3: Test the Package Locally

```bash
# Install in a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the wheel
pip install dist/saastify_edge_sdk-1.0.0-py3-none-any.whl

# Test import
python -c "from saastify_edge.transformations import transform; print(transform('test', 'uppercase'))"

# Should output: TEST

deactivate
rm -rf test_env
```

### Step 4: Check Package Quality

```bash
# Check the distribution
twine check dist/*

# Expected output:
# Checking dist/saastify_edge_sdk-1.0.0.tar.gz: PASSED
# Checking dist/saastify_edge_sdk-1.0.0-py3-none-any.whl: PASSED
```

### Step 5: Upload to Test PyPI (Optional but Recommended)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps saastify-edge-sdk

# Verify it works
python -c "from saastify_edge.transformations import transform; print('OK')"
```

### Step 6: Upload to Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Enter your PyPI credentials when prompted
# Or use token from ~/.pypirc

# Expected output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading saastify_edge_sdk-1.0.0-py3-none-any.whl
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Uploading saastify_edge_sdk-1.0.0.tar.gz
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# View at: https://pypi.org/project/saastify-edge-sdk/
```

### Step 7: Verify Installation

```bash
# Create fresh environment
python -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install saastify-edge-sdk

# Test
python -c "from saastify_edge.transformations import transform; print(transform('hello', 'uppercase'))"

deactivate
rm -rf verify_env
```

### Using the Published Package

```python
# Install
pip install saastify-edge-sdk

# Import and use
from saastify_edge.transformations import transform, bulk_apply_pipe_rules
from saastify_edge.validation import validate_row
from saastify_edge.core.parsers import get_parser
from saastify_edge.export import build_csv, build_xlsx

# Example
result = transform("test", "uppercase")
print(result)  # TEST
```

---

## JavaScript SDK Publishing (npm)

### Step 1: Prepare the Release

```bash
cd js-sdk

# Clean previous builds
rm -rf dist/ node_modules/

# Install dependencies
npm install

# Update version in package.json
# Edit "version": "1.0.1" or use npm version command
```

### Step 2: Build the Package

```bash
# Run TypeScript compiler
npm run build

# Verify dist/ directory is created with all files
ls -la dist/

# Run tests (if available)
npm test

# Run type checking
npm run typecheck

# Run linting
npm run lint
```

### Step 3: Test the Package Locally

```bash
# Create a local tarball
npm pack

# This creates: saastify-edge-sdk-1.0.0.tgz

# Test in another project
cd /tmp
mkdir test-install
cd test-install
npm init -y
npm install /path/to/edge-channel-suite-sdk/js-sdk/saastify-edge-sdk-1.0.0.tgz

# Test import
node -e "const { transform } = require('@saastify/edge-sdk'); console.log(transform('test', 'uppercase'))"

# Should output: TEST
```

### Step 4: Publish to npm

```bash
cd js-sdk

# Login to npm (if not already)
npm login

# Dry run to see what will be published
npm publish --dry-run

# Review the output:
# - Files that will be included
# - package.json details
# - Size of package

# Publish (if using scoped package @saastify, you may need --access public)
npm publish --access public

# Expected output:
# npm notice 
# npm notice 📦  @saastify/edge-sdk@1.0.0
# npm notice === Tarball Contents === 
# npm notice 1.2kB  package.json
# npm notice 2.1kB  README.md
# npm notice 1.1kB  LICENSE
# npm notice ...
# npm notice === Tarball Details === 
# npm notice name:          @saastify/edge-sdk
# npm notice version:       1.0.0
# npm notice filename:      saastify-edge-sdk-1.0.0.tgz
# npm notice package size:  50.2 kB
# npm notice unpacked size: 200.5 kB
# npm notice total files:   45
# npm notice 
# + @saastify/edge-sdk@1.0.0
```

### Step 5: Verify Publication

```bash
# View package on npm
open https://www.npmjs.com/package/@saastify/edge-sdk

# Install from npm in a fresh directory
cd /tmp
mkdir test-npm
cd test-npm
npm init -y
npm install @saastify/edge-sdk

# Test
node -e "const { transform } = require('@saastify/edge-sdk'); console.log(transform('hello', 'uppercase'))"

# Clean up
cd ..
rm -rf test-npm
```

### Using the Published Package

**CommonJS:**
```javascript
const { transform, bulkApplyPipeRules } = require('@saastify/edge-sdk');
const { validateRow } = require('@saastify/edge-sdk/validation');
const { buildCSV } = require('@saastify/edge-sdk/export');

const result = transform('test', 'uppercase');
console.log(result); // TEST
```

**ES Modules:**
```javascript
import { transform, bulkApplyPipeRules } from '@saastify/edge-sdk';
import { validateRow } from '@saastify/edge-sdk/validation';
import { buildCSV } from '@saastify/edge-sdk/export';

const result = transform('test', 'uppercase');
console.log(result); // TEST
```

**TypeScript:**
```typescript
import { transform, bulkApplyPipeRules } from '@saastify/edge-sdk';
import { validateRow, ValidationRules } from '@saastify/edge-sdk/validation';

const result: string = transform('test', 'uppercase');
console.log(result); // TEST
```

---

## Version Management

### Semantic Versioning

Both packages follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version (1.x.x): Incompatible API changes
- **MINOR** version (x.1.x): New functionality (backwards-compatible)
- **PATCH** version (x.x.1): Bug fixes (backwards-compatible)

### Version Bump Scripts

Create a helper script to bump versions:

**`scripts/bump_version.sh`:**
```bash
#!/bin/bash

VERSION_TYPE=$1

if [ -z "$VERSION_TYPE" ]; then
    echo "Usage: ./scripts/bump_version.sh [major|minor|patch]"
    exit 1
fi

# Python SDK
cd python-sdk
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current Python version: $CURRENT_VERSION"

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
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update Python SDK
sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "✓ Updated python-sdk/pyproject.toml"

# Update JavaScript SDK
cd ../js-sdk
npm version $NEW_VERSION --no-git-tag-version
echo "✓ Updated js-sdk/package.json"

cd ..
echo ""
echo "✅ Version bumped to $NEW_VERSION in both SDKs"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Commit: git commit -am \"Bump version to $NEW_VERSION\""
echo "3. Tag: git tag v$NEW_VERSION"
echo "4. Push: git push && git push --tags"
```

**Usage:**
```bash
chmod +x scripts/bump_version.sh
./scripts/bump_version.sh patch   # 1.0.0 -> 1.0.1
./scripts/bump_version.sh minor   # 1.0.0 -> 1.1.0
./scripts/bump_version.sh major   # 1.0.0 -> 2.0.0
```

### Manual Version Update

**Python SDK:**
```bash
# Edit python-sdk/pyproject.toml
version = "1.0.1"
```

**JavaScript SDK:**
```bash
cd js-sdk
npm version patch  # or minor, major
# This automatically updates package.json and creates a git tag
```

---

## CI/CD Automation

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish SDKs

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags like v1.0.0

jobs:
  publish-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        working-directory: python-sdk
        run: python -m build
      
      - name: Publish to PyPI
        working-directory: python-sdk
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*

  publish-javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Install dependencies
        working-directory: js-sdk
        run: npm ci
      
      - name: Build package
        working-directory: js-sdk
        run: npm run build
      
      - name: Publish to npm
        working-directory: js-sdk
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npm publish --access public
```

### Setup GitHub Secrets

1. Go to your repository settings
2. Navigate to Secrets and variables → Actions
3. Add secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `NPM_TOKEN`: Your npm access token

### Automated Release Process

```bash
# 1. Bump version
./scripts/bump_version.sh minor

# 2. Commit and tag
git add .
git commit -m "Release v1.1.0"
git tag v1.1.0

# 3. Push (triggers CI/CD)
git push origin main
git push origin v1.1.0

# GitHub Actions will automatically:
# - Build both packages
# - Run tests
# - Publish to PyPI and npm
```

---

## Troubleshooting

### Python SDK Issues

**Issue: "Invalid distribution" error**
```bash
# Solution: Check MANIFEST.in and ensure all files are included
python -m build
twine check dist/*
```

**Issue: "Package already exists"**
```bash
# Solution: Bump version number in pyproject.toml
# PyPI doesn't allow overwriting published versions
```

**Issue: "Authentication failed"**
```bash
# Solution: Verify your ~/.pypirc or use token directly
twine upload -u __token__ -p pypi-YOUR_TOKEN dist/*
```

### JavaScript SDK Issues

**Issue: "403 Forbidden - You do not have permission"**
```bash
# Solution: 
# 1. Verify you're logged in: npm whoami
# 2. For scoped packages, use: npm publish --access public
# 3. Request access to @saastify organization
```

**Issue: "Package name too similar to existing package"**
```bash
# Solution: Choose a different package name or request name transfer
# Check availability: npm view @saastify/edge-sdk
```

**Issue: "Module not found" after installation**
```bash
# Solution: Verify exports in package.json match dist/ structure
# Rebuild: npm run build
# Test: npm pack && npm install saastify-edge-sdk-1.0.0.tgz
```

### General Issues

**Issue: Version mismatch between Python and JavaScript**
```bash
# Solution: Use bump_version.sh script to update both simultaneously
./scripts/bump_version.sh patch
```

**Issue: Missing dependencies after install**
```bash
# Python: Check dependencies in pyproject.toml
# JavaScript: Check dependencies in package.json and ensure they're not in devDependencies
```

---

## Using in N8N

### Installation in N8N

N8N supports custom npm packages. To use the JavaScript SDK:

1. **In N8N Cloud/Self-hosted:**
   ```javascript
   // In a Function node
   const { transform } = require('@saastify/edge-sdk');
   
   const items = $input.all();
   
   return items.map(item => ({
     json: {
       sku: transform(item.json.sku, 'strip + uppercase'),
       name: transform(item.json.name, 'title_case'),
       price: transform(item.json.price, 'clean_numeric_value + round_decimal|2')
     }
   }));
   ```

2. **With npm package installation:**
   - N8N automatically installs packages used in Function nodes
   - Or manually install in N8N environment:
     ```bash
     cd ~/.n8n
     npm install @saastify/edge-sdk
     ```

---

## Support

- **Issues**: https://github.com/demystify-systems/edge-channel-suite-sdk/issues
- **Documentation**: See `/docs` in repository
- **Examples**: See `/examples` in repository

## License

MIT License - See LICENSE file for details
