# Running Notebooks with Papermill

This guide explains how to run the Jupyter notebooks using Papermill for parameterized execution.

---

## Installation

```bash
# Install papermill
pip install papermill

# Install notebook dependencies
pip install jupyter ipykernel

# Install SDK (if not already installed)
pip install saastify-edge-sdk

# Install GCS dependencies (for GCS operations)
pip install google-cloud-storage
```

---

## Running Import Notebook

### Basic Usage

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
    -p feed_settings_json '{"skip_errors": false, "update_products": true, "validate_products": true}'
```

### With Environment Variables

```bash
# Set environment variables
export DB_MODE=direct
export DB_INSTANCE=my-project:us-central1:my-instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export SAAS_EDGE_ID=tenant-123

# Run notebook
papermill \
    examples/python/collectionsImport.ipynb \
    output/import-result.ipynb \
    -p file_url "gs://my-bucket/imports/products.csv" \
    -p file_name "products.csv" \
    -p job_name "Collections Import" \
    -p template_id "collections-template-001" \
    -p import_type "collections"
```

### Using Parameter File

Create `import-params.json`:

```json
{
  "file_url": "https://storage.googleapis.com/edge-assets/.../products.csv",
  "file_name": "products.csv",
  "job_name": "Collections Import - Products",
  "template_id": "collections-template-001",
  "saas_edge_id": "tenant-123",
  "import_type": "collections",
  "feed_settings_json": "{\"skip_errors\": false, \"update_products\": true, \"validate_products\": true, \"create_new_collection\": true}"
}
```

Run with parameter file:

```bash
papermill \
    examples/python/collectionsImport.ipynb \
    output/import-result.ipynb \
    -f import-params.json
```

---

## Running Export Notebook

### Basic Usage

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
    -p product_filters_json '{"status": "active", "category": "Electronics"}'
```

### With Environment Variables

```bash
# Set environment variables (same as import)
export DB_MODE=direct
export DB_INSTANCE=my-project:us-central1:my-instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Run notebook
papermill \
    examples/python/collectionsExport.ipynb \
    output/export-result.ipynb \
    -p template_id "collections-template-001" \
    -p saas_edge_id "tenant-123" \
    -p output_bucket "my-bucket" \
    -p output_path "exports/products.csv" \
    -p file_format "csv"
```

---

## Extracting Results

After running with Papermill, extract results from the executed notebook:

```python
import json
import nbformat

# Read executed notebook
with open("output/import-result.ipynb", "r") as f:
    nb = nbformat.read(f, as_version=4)

# Find the summary cell (last cell with output)
for cell in reversed(nb.cells):
    if cell.cell_type == "code" and cell.outputs:
        # Look for JSON output
        for output in cell.outputs:
            if "text" in output and "Summary JSON" in output.get("text", ""):
                # Extract JSON
                lines = output["text"].split("\\n")
                json_start = False
                json_lines = []
                for line in lines:
                    if "{" in line:
                        json_start = True
                    if json_start:
                        json_lines.append(line)
                summary_json = "\\n".join(json_lines)
                summary = json.loads(summary_json)
                print(f"Job ID: {summary['job_id']}")
                print(f"Status: {summary['status']}")
                break
```

---

## Integration with Job Scheduler

### Example: Cloud Scheduler + Cloud Run

Create a Cloud Run job that runs the notebook:

```python
# cloud_run_job.py
import os
import papermill as pm

def run_import_job(request):
    """Cloud Run function to execute import notebook."""
    
    # Get parameters from request
    params = request.get_json()
    
    # Set environment variables from Cloud Run secrets
    os.environ["DB_MODE"] = os.getenv("DB_MODE", "direct")
    os.environ["DB_INSTANCE"] = os.getenv("DB_INSTANCE")
    os.environ["DB_NAME"] = os.getenv("DB_NAME")
    os.environ["DB_USER"] = os.getenv("DB_USER")
    os.environ["DB_PASSWORD"] = os.getenv("DB_PASSWORD")
    
    # Run notebook
    pm.execute_notebook(
        "examples/python/collectionsImport.ipynb",
        "/tmp/output.ipynb",
        parameters=params
    )
    
    return {"status": "completed"}
```

---

## Best Practices

1. **Always set environment variables** before running notebooks
2. **Use parameter files** for complex configurations
3. **Store output notebooks** for audit trail
4. **Extract results** programmatically from executed notebooks
5. **Handle errors** - Papermill will raise exceptions on notebook failures
6. **Use secrets management** for sensitive credentials (Cloud Secret Manager, etc.)

---

## Troubleshooting

### Notebook Execution Fails

```bash
# Run with verbose output
papermill \
    examples/python/collectionsImport.ipynb \
    output/result.ipynb \
    --log-output \
    --log-level DEBUG
```

### Database Connection Issues

```bash
# Test database connection first
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

### GCS Access Issues

```bash
# Test GCS access
python -c "
from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print('Buckets:', [b.name for b in buckets])
"
```

---

For more information, see the `PACKAGE_USAGE_GUIDE.md` for detailed configuration instructions.

