# Quick Publishing Guide

## One-Time Setup

### Python (PyPI)

1. Install tools:
   ```bash
   pip install --upgrade build twine
   ```

2. Create PyPI account: https://pypi.org/account/register/

3. Get API token: https://pypi.org/manage/account/token/

4. Configure credentials:
   ```bash
   echo "[pypi]
   username = __token__
   password = pypi-YOUR_TOKEN_HERE" > ~/.pypirc
   chmod 600 ~/.pypirc
   ```

### JavaScript (npm)

1. Create npm account: https://www.npmjs.com/signup

2. Login:
   ```bash
   npm login
   ```

### GitHub Actions (Optional Automation)

1. Go to repository settings → Secrets → Actions
2. Add secrets:
   - `PYPI_API_TOKEN` - Your PyPI token
   - `NPM_TOKEN` - Your npm token

## Publishing Methods

### Method 1: Automated Release (Recommended)

```bash
# Bump version and release in one command
./scripts/release.sh 1.0.1

# This will:
# - Update version in both SDKs
# - Commit changes
# - Create git tag
# - Push to GitHub
# - Trigger CI/CD (if configured)
```

### Method 2: Manual Step-by-Step

```bash
# 1. Bump version
./scripts/bump_version.sh patch  # or minor, major

# 2. Review changes
git diff

# 3. Commit and tag
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1

# 4. Push
git push origin main
git push origin v1.0.1

# 5. Publish Python SDK
./scripts/publish_python.sh

# 6. Publish JavaScript SDK
./scripts/publish_npm.sh
```

### Method 3: Individual SDK Publishing

**Python only:**
```bash
cd python-sdk
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*
```

**JavaScript only:**
```bash
cd js-sdk
npm run build
npm publish --access public
```

## Quick Commands Reference

```bash
# Version management
./scripts/bump_version.sh patch   # 1.0.0 → 1.0.1
./scripts/bump_version.sh minor   # 1.0.0 → 1.1.0
./scripts/bump_version.sh major   # 1.0.0 → 2.0.0

# Full release
./scripts/release.sh 1.0.1

# Publish individually
./scripts/publish_python.sh
./scripts/publish_npm.sh
```

## Verify Published Packages

**Python:**
```bash
pip install saastify-edge-sdk
python -c "from saastify_edge.transformations import transform; print(transform('test', 'uppercase'))"
```

**JavaScript:**
```bash
npm install @saastify/edge-sdk
node -e "const {transform} = require('@saastify/edge-sdk'); console.log(transform('test', 'uppercase'))"
```

## Package URLs

- **PyPI**: https://pypi.org/project/saastify-edge-sdk/
- **npm**: https://www.npmjs.com/package/@saastify/edge-sdk

## Need Help?

See full guide: [PUBLISHING.md](./PUBLISHING.md)
