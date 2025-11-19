# Jupyter Notebooks for Import and Export Jobs

This directory contains production-ready Jupyter notebooks for running import and export jobs using the SaaStify Edge SDK.

---

## 📚 Notebooks

### 1. `collectionsImport.ipynb`
**Purpose**: Import product data from CSV/XLSX/JSON/XML files into the database.

**Features**:
- ✅ Uses published `saastify-edge-sdk` package
- ✅ Real database connections (PostgreSQL/Cloud SQL)
- ✅ Real GCS file loading (no mocks)
- ✅ Parameterized for Papermill execution
- ✅ Handles your exact import job request structure
- ✅ Writes products to database after validation

**Parameters**:
- `file_url`: URL to import file (HTTP or GCS)
- `file_name`: Name of the file
- `job_name`: Name of the import job
- `template_id`: Template ID (optional, will be looked up)
- `saas_edge_id`: Tenant identifier
- `import_type`: Type of import (e.g., "collections")
- `feed_settings_json`: JSON string with feed settings

### 2. `collectionsExport.ipynb`
**Purpose**: Export product data from database to CSV/XLSX/JSON/XML files.

**Features**:
- ✅ Uses published `saastify-edge-sdk` package
- ✅ Real database connections (PostgreSQL/Cloud SQL)
- ✅ Fetches products from database
- ✅ Uploads to GCS bucket
- ✅ Parameterized for Papermill execution

**Parameters**:
- `template_id`: Template ID for export mapping
- `saas_edge_id`: Tenant identifier
- `output_bucket`: GCS bucket name
- `output_path`: Path within bucket
- `file_format`: Output format (csv, tsv, xlsx, json, xml)
- `job_name`: Name of the export job
- `product_filters_json`: JSON string with product filters

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install SDK
pip install saastify-edge-sdk

# Install notebook dependencies
pip install jupyter ipykernel papermill

# Install GCS dependencies
pip install google-cloud-storage
```

### 2. Set Environment Variables

```bash
# Database configuration
export DB_MODE=direct  # or "proxy" or "local"
export DB_INSTANCE=my-project:us-central1:my-instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password

# GCS credentials (optional, uses ADC if not set)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 3. Run Import Notebook

```bash
papermill \
    examples/python/collectionsImport.ipynb \
    output/import-result.ipynb \
    -p file_url "https://storage.googleapis.com/edge-assets/.../products.csv" \
    -p file_name "products.csv" \
    -p job_name "Collections Import - Products" \
    -p template_id "collections-template-001" \
    -p saas_edge_id "tenant-123" \
    -p import_type "collections" \
    -p feed_settings_json '{"skip_errors": false, "update_products": true, "validate_products": true, "create_new_collection": true}'
```

### 4. Run Export Notebook

```bash
papermill \
    examples/python/collectionsExport.ipynb \
    output/export-result.ipynb \
    -p template_id "collections-template-001" \
    -p saas_edge_id "tenant-123" \
    -p output_bucket "edge-assets" \
    -p output_path "exports/collections/products.csv" \
    -p file_format "csv" \
    -p job_name "Collections Export" \
    -p product_filters_json '{"status": "active"}'
```

---

## 📖 Detailed Documentation

- **Package Usage Guide**: See `PACKAGE_USAGE_GUIDE.md` for:
  - Installing the SDK as a package
  - Configuring environment variables
  - Database connection setup
  - GCS configuration
  - Real implementation examples

- **Papermill Usage**: See `PAPERMILL_USAGE.md` for:
  - Running notebooks with Papermill
  - Parameter files
  - Extracting results
  - Integration with schedulers

---

## 🔧 Configuration

### Database Connection Modes

#### Direct Cloud SQL (Production)
```bash
export DB_MODE=direct
export DB_INSTANCE=project:region:instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
```

#### Cloud SQL Proxy (Local Development)
```bash
# Start proxy first:
cloud-sql-proxy my-project:us-central1:my-instance

# Then set:
export DB_MODE=proxy
export DB_PROXY_HOST=localhost
export DB_PROXY_PORT=5432
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
```

#### Local PostgreSQL
```bash
export DB_MODE=local
export DB_LOCAL_HOST=localhost
export DB_LOCAL_PORT=5432
export DB_NAME=saastify_edge_dev
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### GCS Configuration

The SDK automatically uses:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (if set)
2. Application Default Credentials (ADC) on GCP
3. Service account attached to Compute Engine/Cloud Run/GKE

---

## 📝 Example Import Job Request

The import notebook matches your exact request structure:

```json
{
    "file_url": {
        "url": "https://storage.googleapis.com/edge-assets/.../products.csv",
        "file_name": "products.csv"
    },
    "job_name": "Collections Import - Products",
    "job_path": "saastify-internal/catalog-edge/collectionsImport.ipynb",
    "import_type": "collections",
    "template_id": null,
    "feed_settings": {
        "skip_errors": false,
        "maintain_order": true,
        "update_products": true,
        "validate_products": true,
        "notification_email": "user@example.com",
        "create_new_collection": true
    }
}
```

**Papermill equivalent**:
```bash
papermill collectionsImport.ipynb output.ipynb \
    -p file_url "https://storage.googleapis.com/..." \
    -p file_name "products.csv" \
    -p job_name "Collections Import - Products" \
    -p import_type "collections" \
    -p feed_settings_json '{"skip_errors": false, "update_products": true, ...}'
```

---

## 🎯 Key Features

### ✅ No Mocks
- Real database connections using PostgreSQLClient
- Real GCS file operations
- Real product upserts to database
- Real product fetching from database

### ✅ Production Ready
- Error handling and retry logic
- Structured logging
- Job tracking and metrics
- Completeness cache integration

### ✅ Flexible
- Supports HTTP, GCS, S3, and local files
- Multiple file formats (CSV, TSV, XLSX, JSON, XML)
- Configurable batch sizes and workers
- Customizable product filters

---

## 🐛 Troubleshooting

### Import Errors

**Database connection fails**:
```bash
# Test connection
python -c "
from saastify_edge.db import PostgreSQLClient, get_db_config
import asyncio
async def test():
    db = PostgreSQLClient(get_db_config())
    await db.connect()
    print('Connected:', await db.health_check())
    await db.disconnect()
asyncio.run(test())
"
```

**GCS access denied**:
```bash
# Test GCS access
python -c "
from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print('Buckets:', [b.name for b in buckets])
"
```

**SDK not found**:
```bash
# Verify installation
pip show saastify-edge-sdk

# Reinstall if needed
pip install --force-reinstall saastify-edge-sdk
```

---

## 📚 Additional Resources

- **Main README**: `/README.md` - Overview of the SDK
- **Python SDK README**: `/python-sdk/README.md` - Python-specific documentation
- **Examples**: `/examples/python/import_example.py` and `export_example.py` - Basic examples

---

## 💡 Tips

1. **Always set environment variables** before running notebooks
2. **Use parameter files** for complex configurations
3. **Store output notebooks** for audit trail
4. **Extract results** programmatically from executed notebooks
5. **Use secrets management** for production (Cloud Secret Manager, etc.)

---

For more information, see:
- `PACKAGE_USAGE_GUIDE.md` - Detailed package usage
- `PAPERMILL_USAGE.md` - Papermill execution guide

