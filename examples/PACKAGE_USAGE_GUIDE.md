# Using SaaStify Edge SDK as a Published Package

This guide explains how to use the `saastify-edge-sdk` package in a different repository for production jobs, including configuring real database and GCS connections.

---

## 1. Installing the Published Package

### From PyPI (After Publishing)

```bash
pip install saastify-edge-sdk
```

### From GitHub (Development/Private)

```bash
pip install git+https://github.com/demystify-systems/edge-channel-suite-sdk.git@main#subdirectory=python-sdk
```

### With Specific Version

```bash
pip install saastify-edge-sdk==1.0.0
```

### In requirements.txt

```txt
saastify-edge-sdk>=1.0.0
```

---

## 2. Importing the SDK

### Basic Import

```python
# Import the SDK package
from saastify_edge import (
    ImportPipelineConfig,
    ExportPipelineConfig,
    run_product_import,
    run_product_export
)

# Import database clients
from saastify_edge.db import (
    PostgreSQLClient,
    DatabaseConfig,
    get_db_config
)

# Import file loaders
from saastify_edge.core.loaders import FileLoaderFactory

# Import utilities
from saastify_edge.utils import setup_logging
```

### Verify Installation

```python
import saastify_edge
print(saastify_edge.__version__)  # Should print version number
```

---

## 3. Environment Variables Configuration

### Database Connection

The SDK uses environment variables for database configuration. Set these before running your jobs:

#### Production (Direct Cloud SQL Connection)

```bash
# Connection mode
export DB_MODE=direct

# Cloud SQL instance (format: project:region:instance)
export DB_INSTANCE=my-project:us-central1:my-instance

# Database credentials
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-secure-password

# Connection pool settings
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=20

# SSL settings
export DB_USE_SSL=true
```

#### Local Development (Cloud SQL Proxy)

```bash
# Start Cloud SQL Proxy first:
# cloud-sql-proxy my-project:us-central1:my-instance

# Then set environment variables:
export DB_MODE=proxy
export DB_PROXY_HOST=localhost
export DB_PROXY_PORT=5432
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
export DB_USE_SSL=false
```

#### Local PostgreSQL

```bash
export DB_MODE=local
export DB_LOCAL_HOST=localhost
export DB_LOCAL_PORT=5432
export DB_NAME=saastify_edge_dev
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_USE_SSL=false
```

### Google Cloud Storage (GCS)

For GCS file operations, the SDK uses Google Cloud credentials:

#### Option 1: Service Account JSON (Recommended for Production)

```bash
# Set path to service account JSON file
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Or pass directly in code (see examples below)
```

#### Option 2: Application Default Credentials (ADC)

If running on GCP (Cloud Run, GKE, Compute Engine), ADC is automatically used:

```bash
# No additional configuration needed
# The SDK will use the service account attached to the instance
```

#### Option 3: User Credentials (Local Development)

```bash
# Authenticate with your user account
gcloud auth application-default login
```

### AWS S3 (Alternative)

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

---

## 4. Creating Database Client

### Using Environment Variables (Recommended)

```python
from saastify_edge.db import PostgreSQLClient, get_db_config

# Get config from environment variables
db_config = get_db_config()

# Create and connect client
db_client = PostgreSQLClient(db_config)
await db_client.connect()

# Use in pipelines
# ... (see examples below)
```

### Manual Configuration

```python
from saastify_edge.db import PostgreSQLClient, DatabaseConfig, ConnectionMode

# Create custom config
db_config = DatabaseConfig(
    mode=ConnectionMode.DIRECT,
    instance_connection_name="my-project:us-central1:my-instance",
    database="saastify_edge",
    user="postgres",
    password="your-password",
    pool_size=10,
    use_ssl=True
)

db_client = PostgreSQLClient(db_config)
await db_client.connect()
```

---

## 5. Real Import Job Example

### Complete Import Pipeline with Real DB and GCS

```python
import asyncio
import os
from saastify_edge import ImportPipelineConfig, run_product_import
from saastify_edge.db import PostgreSQLClient, get_db_config
from saastify_edge.utils import setup_logging

# Setup logging
setup_logging(level="INFO", structured=True)

async def run_real_import():
    """Run import job with real database and GCS connections."""
    
    # Initialize database client from environment
    db_config = get_db_config()
    db_client = PostgreSQLClient(db_config)
    await db_client.connect()
    
    try:
        # Configure import pipeline
        config = ImportPipelineConfig(
            file_source="gs://my-bucket/imports/products.csv",  # GCS URL
            template_id="amazon-template-001",
            saas_edge_id="tenant-123",
            job_name="Collections Import - Products",
            batch_size=500,
            max_workers=4,
            file_loader_config={
                # GCS credentials (if not using ADC)
                # "gcs_credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            },
            db_client=db_client  # Real database client
        )
        
        # Run import pipeline
        results = await run_product_import(config)
        
        print(f"Import completed:")
        print(f"  Total rows: {results['total_processed']}")
        print(f"  Valid rows: {results['total_processed'] - results['total_errors']}")
        print(f"  Error rows: {results['total_errors']}")
        print(f"  Job ID: {results.get('job_id')}")
        
        return results
        
    finally:
        # Cleanup
        await db_client.disconnect()

# Run
if __name__ == "__main__":
    asyncio.run(run_real_import())
```

### Handling Import Job Request (from your example)

```python
import asyncio
import os
from saastify_edge import ImportPipelineConfig, run_product_import
from saastify_edge.db import PostgreSQLClient, get_db_config

async def handle_import_request(request_data: dict):
    """
    Handle import job request matching your API structure.
    
    Request structure:
    {
        "file_url": {
            "url": "https://storage.googleapis.com/...",
            "file_name": "products.csv"
        },
        "job_name": "Collections Import",
        "template_id": "template-123",
        "feed_settings": {
            "skip_errors": false,
            "update_products": true,
            "validate_products": true,
            ...
        }
    }
    """
    
    # Initialize database client
    db_config = get_db_config()
    db_client = PostgreSQLClient(db_config)
    await db_client.connect()
    
    try:
        # Extract request data
        file_url = request_data["file_url"]["url"]
        job_name = request_data["job_name"]
        template_id = request_data.get("template_id")
        feed_settings = request_data.get("feed_settings", {})
        
        # Configure import pipeline
        config = ImportPipelineConfig(
            file_source=file_url,  # HTTP URL or gs:// URL
            template_id=template_id,
            saas_edge_id=os.getenv("SAAS_EDGE_ID", "default-tenant"),  # From env or request
            job_name=job_name,
            batch_size=500,
            max_workers=4,
            file_loader_config={
                # GCS credentials if needed
                # "gcs_credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            },
            db_client=db_client
        )
        
        # Run import
        results = await run_product_import(config)
        
        return {
            "job_id": results.get("job_id"),
            "status": "completed",
            "total_rows": results["total_processed"],
            "valid_rows": results["total_processed"] - results["total_errors"],
            "error_rows": results["total_errors"],
            "feed_settings_applied": feed_settings
        }
        
    finally:
        await db_client.disconnect()

# Example usage
request = {
    "file_url": {
        "url": "https://storage.googleapis.com/edge-assets/b6b2785c-5a16-4744-b726-4b18eadc2024/imports/collections/selected-products-export-2025-11-12__1_.csv",
        "file_name": "selected-products-export-2025-11-12 (1).csv"
    },
    "job_name": "Collections Import - selected-products-export-2025-11-12 (1)",
    "template_id": "collections-template-001",
    "feed_settings": {
        "skip_errors": False,
        "maintain_order": True,
        "update_products": True,
        "validate_products": True,
        "create_new_collection": True
    }
}

# Run
# results = asyncio.run(handle_import_request(request))
```

---

## 6. Real Export Job Example

### Complete Export Pipeline with Real DB and GCS Upload

```python
import asyncio
import os
from saastify_edge import ExportPipelineConfig, run_product_export
from saastify_edge.db import PostgreSQLClient, get_db_config

async def run_real_export():
    """Run export job with real database and GCS upload."""
    
    # Initialize database client
    db_config = get_db_config()
    db_client = PostgreSQLClient(db_config)
    await db_client.connect()
    
    try:
        # Configure export pipeline
        config = ExportPipelineConfig(
            template_id="amazon-template-001",
            saas_edge_id="tenant-123",
            output_path="gs://my-bucket/exports/products.csv",  # GCS output path
            file_format="csv",
            job_name="Products Export - Amazon",
            product_filters={
                # Filter products (would be implemented in DB query)
                "status": "active",
                "category": "Electronics"
            },
            file_config={
                "delimiter": ",",
                "include_headers": True
            },
            reuse_cache=True,
            db_client=db_client
        )
        
        # Run export pipeline
        results = await run_product_export(config)
        
        print(f"Export completed:")
        print(f"  Output path: {results['output_path']}")
        print(f"  Total rows: {results['total_rows']}")
        print(f"  Job ID: {results['job_id']}")
        
        return results
        
    finally:
        await db_client.disconnect()

# Run
# asyncio.run(run_real_export())
```

---

## 7. GCS Upload Implementation

The SDK's file builders create local files. To upload to GCS, add this helper:

```python
import asyncio
from google.cloud import storage
from pathlib import Path

async def upload_to_gcs(
    local_file_path: str,
    gcs_bucket: str,
    gcs_path: str,
    credentials_path: Optional[str] = None
) -> str:
    """
    Upload file to Google Cloud Storage.
    
    Args:
        local_file_path: Path to local file
        gcs_bucket: GCS bucket name
        gcs_path: Path within bucket (e.g., "exports/products.csv")
        credentials_path: Optional path to service account JSON
        
    Returns:
        GCS URL (gs://bucket/path)
    """
    try:
        from google.cloud import storage
    except ImportError:
        raise ImportError("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
    
    # Initialize client
    if credentials_path:
        client = storage.Client.from_service_account_json(credentials_path)
    else:
        client = storage.Client()  # Uses ADC or GOOGLE_APPLICATION_CREDENTIALS
    
    # Upload file
    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(gcs_path)
    
    await asyncio.to_thread(blob.upload_from_filename, local_file_path)
    
    gcs_url = f"gs://{gcs_bucket}/{gcs_path}"
    print(f"Uploaded to {gcs_url}")
    
    return gcs_url

# Usage in export pipeline
async def export_and_upload():
    """Export and upload to GCS."""
    
    # ... run export pipeline (creates local file) ...
    
    # Upload to GCS
    gcs_url = await upload_to_gcs(
        local_file_path="/tmp/export.csv",
        gcs_bucket="my-bucket",
        gcs_path="exports/products.csv"
    )
    
    return gcs_url
```

---

## 8. Fetching Products from Database

To implement real product fetching in export pipeline, you need to query your database:

```python
async def fetch_products_from_db(
    db_client: PostgreSQLClient,
    saas_edge_id: str,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Fetch products from database for export.
    
    Args:
        db_client: Database client
        saas_edge_id: Tenant identifier
        filters: Optional filters (status, category, etc.)
        
    Returns:
        List of product dictionaries
    """
    filters = filters or {}
    
    # Build query
    query = """
        SELECT 
            product_id,
            product_title,
            selling_price,
            stock_qty,
            product_sku,
            product_description,
            category,
            brand,
            created_at,
            updated_at
        FROM products
        WHERE saas_edge_id = $1
    """
    
    params = [saas_edge_id]
    param_idx = 2
    
    # Add filters
    if filters.get("status"):
        query += f" AND status = ${param_idx}"
        params.append(filters["status"])
        param_idx += 1
    
    if filters.get("category"):
        query += f" AND category = ${param_idx}"
        params.append(filters["category"])
        param_idx += 1
    
    query += " ORDER BY created_at DESC LIMIT 10000"
    
    # Execute query
    products = await db_client.fetch_all(query, *params)
    
    return products

# Use in export pipeline
async def run_export_with_db_fetch():
    """Export with real database product fetch."""
    
    db_config = get_db_config()
    db_client = PostgreSQLClient(db_config)
    await db_client.connect()
    
    try:
        # Fetch products
        products = await fetch_products_from_db(
            db_client=db_client,
            saas_edge_id="tenant-123",
            filters={"status": "active"}
        )
        
        # Now use these products in export pipeline
        # (You may need to modify ExportPipeline to accept pre-fetched products)
        
    finally:
        await db_client.disconnect()
```

---

## 9. Writing Products to Database

To implement real product upsert in import pipeline:

```python
async def upsert_products_to_db(
    db_client: PostgreSQLClient,
    products: List[Dict[str, Any]],
    saas_edge_id: str,
    feed_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Upsert products to database after import validation.
    
    Args:
        db_client: Database client
        products: List of validated product dictionaries
        saas_edge_id: Tenant identifier
        feed_settings: Feed settings (update_products, create_new_product, etc.)
        
    Returns:
        Upsert results
    """
    upserted_count = 0
    created_count = 0
    updated_count = 0
    errors = []
    
    for product in products:
        try:
            # Check if product exists
            existing = await db_client.fetch_one(
                """
                SELECT product_id FROM products 
                WHERE saas_edge_id = $1 AND product_sku = $2
                """,
                saas_edge_id,
                product.get("product_sku")
            )
            
            if existing:
                # Update existing product
                if feed_settings.get("update_products", True):
                    await db_client.update(
                        "products",
                        {
                            "saas_edge_id": saas_edge_id,
                            "product_sku": product.get("product_sku")
                        },
                        {
                            "product_title": product.get("product_title"),
                            "selling_price": product.get("selling_price"),
                            "stock_qty": product.get("stock_qty"),
                            "product_description": product.get("product_description"),
                            "updated_at": "NOW()"
                        }
                    )
                    updated_count += 1
            else:
                # Create new product
                if feed_settings.get("create_new_product", True):
                    await db_client.insert("products", {
                        "product_id": str(uuid.uuid4()),
                        "saas_edge_id": saas_edge_id,
                        "product_sku": product.get("product_sku"),
                        "product_title": product.get("product_title"),
                        "selling_price": product.get("selling_price"),
                        "stock_qty": product.get("stock_qty"),
                        "product_description": product.get("product_description"),
                        "created_at": "NOW()",
                        "updated_at": "NOW()"
                    })
                    created_count += 1
            
            upserted_count += 1
            
        except Exception as e:
            if not feed_settings.get("skip_errors", False):
                raise
            errors.append({
                "product": product.get("product_sku"),
                "error": str(e)
            })
    
    return {
        "upserted": upserted_count,
        "created": created_count,
        "updated": updated_count,
        "errors": errors
    }
```

---

## 10. Environment Variables Summary

### Required for Production

```bash
# Database
export DB_MODE=direct
export DB_INSTANCE=project:region:instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password

# GCS (if using GCS)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Tenant ID
export SAAS_EDGE_ID=tenant-123
```

### Optional

```bash
# Connection pool
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=20

# SSL
export DB_USE_SSL=true

# AWS (if using S3)
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

---

## 11. Using in Jupyter Notebooks with Papermill

See the `.ipynb` notebooks in this directory for parameterized examples that work with Papermill.

### Running with Papermill

```bash
# Install papermill
pip install papermill

# Run import notebook
papermill \
    examples/python/collectionsImport.ipynb \
    output.ipynb \
    -p file_url "https://storage.googleapis.com/..." \
    -p job_name "Collections Import" \
    -p template_id "template-123" \
    -p saas_edge_id "tenant-123"
```

---

## 12. Troubleshooting

### Database Connection Issues

```python
# Test database connection
from saastify_edge.db import PostgreSQLClient, get_db_config

db_config = get_db_config()
db_client = PostgreSQLClient(db_config)

try:
    await db_client.connect()
    healthy = await db_client.health_check()
    print(f"Database healthy: {healthy}")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    await db_client.disconnect()
```

### GCS Access Issues

```python
# Test GCS access
from google.cloud import storage

client = storage.Client()
buckets = list(client.list_buckets())
print(f"Accessible buckets: {[b.name for b in buckets]}")
```

### Package Import Issues

```bash
# Verify package installation
pip show saastify-edge-sdk

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall if needed
pip install --force-reinstall saastify-edge-sdk
```

---

## 13. Next Steps

1. **Install the package** in your project repository
2. **Set environment variables** for database and GCS
3. **Use the notebooks** as templates for your jobs
4. **Customize** product fetching and upsert logic for your schema
5. **Deploy** to Cloud Run or your execution environment

For more examples, see the `.ipynb` notebooks in this directory.

