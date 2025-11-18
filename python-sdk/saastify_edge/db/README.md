## Database Configuration

The SDK supports three connection modes for PostgreSQL databases:

### 1. **Cloud SQL Proxy** (Local Development) - Default
Use when developing locally with Cloud SQL Proxy running.

```bash
# Start Cloud SQL Proxy
cloud-sql-proxy my-project:us-central1:my-instance

# Set environment variables
export DB_MODE=proxy
export DB_PROXY_HOST=localhost
export DB_PROXY_PORT=5432
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-password
```

### 2. **Direct Connection** (Production)
Use when running in GCP (Cloud Run, GKE, etc.) with direct Cloud SQL access.

```bash
export DB_MODE=direct
export DB_INSTANCE=my-project:us-central1:my-instance
export DB_NAME=saastify_edge
export DB_USER=postgres
export DB_PASSWORD=your-secure-password
export DB_USE_SSL=true
```

### 3. **Local PostgreSQL** (Local Testing)
Use when running a local PostgreSQL instance for testing.

```bash
export DB_MODE=local
export DB_LOCAL_HOST=localhost
export DB_LOCAL_PORT=5432
export DB_NAME=saastify_edge_dev
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_USE_SSL=false
```

## Usage

### Basic Usage

```python
from saastify_edge.db import PostgreSQLClient, get_db_config

# Create client (reads from environment)
client = PostgreSQLClient()
await client.connect()

# Insert data
await client.insert("saas_edge_jobs", {
    "job_id": "123",
    "job_name": "Test Job",
    "job_type": "IMPORT",
    "saas_edge_id": "tenant-001"
})

# Query data
jobs = await client.query("saas_edge_jobs", {"saas_edge_id": "tenant-001"})

# Update data
await client.update(
    "saas_edge_jobs",
    filters={"job_id": "123"},
    updates={"job_status": "COMPLETED"}
)

# Close connection
await client.disconnect()
```

### Using with Import/Export Pipelines

```python
from saastify_edge.db import create_db_client
from saastify_edge.import_pipeline import ImportPipelineConfig, run_product_import

# Create database client
db_client = await create_db_client()

# Configure import with real database
config = ImportPipelineConfig(
    file_source="path/to/products.csv",
    template_id="template-123",
    saas_edge_id="tenant-001",
    db_client=db_client,
)

# Run import
results = await run_product_import(config)
```

### Custom Configuration

```python
from saastify_edge.db import DatabaseConfig, PostgreSQLClient, ConnectionMode

# Custom configuration
config = DatabaseConfig(
    mode=ConnectionMode.PROXY,
    proxy_host="localhost",
    proxy_port=5432,
    database="my_database",
    user="my_user",
    password="my_password",
    pool_size=20,
)

client = PostgreSQLClient(config)
await client.connect()
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_MODE` | Connection mode: `direct`, `proxy`, or `local` | `proxy` |
| `DB_INSTANCE` | GCP instance name (format: `project:region:instance`) | - |
| `DB_NAME` | Database name | `saastify_edge` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | - |
| `DB_PROXY_HOST` | Proxy host for local development | `localhost` |
| `DB_PROXY_PORT` | Proxy port | `5432` |
| `DB_LOCAL_HOST` | Local PostgreSQL host | `localhost` |
| `DB_LOCAL_PORT` | Local PostgreSQL port | `5432` |
| `DB_POOL_SIZE` | Connection pool size | `10` |
| `DB_MAX_OVERFLOW` | Max pool overflow | `20` |
| `DB_USE_SSL` | Enable SSL connections | `true` |

## Testing Database Configuration

```bash
# Test current configuration
cd python-sdk
PYTHONPATH=. python saastify_edge/db/config.py

# Test PostgreSQL connection
PYTHONPATH=. python saastify_edge/db/postgres_client.py
```

## Docker Compose Setup (Local Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: saastify_edge_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Start local PostgreSQL
docker-compose up -d

# Set environment for local mode
export DB_MODE=local
export DB_NAME=saastify_edge_dev
export DB_PASSWORD=postgres
```

## Production Deployment

### Cloud Run

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: edge-import-service
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cloudsql-instances: my-project:us-central1:my-instance
    spec:
      containers:
      - image: gcr.io/my-project/edge-sdk:latest
        env:
        - name: DB_MODE
          value: "direct"
        - name: DB_INSTANCE
          value: "my-project:us-central1:my-instance"
        - name: DB_NAME
          value: "saastify_edge"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

### GKE

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-import
spec:
  template:
    spec:
      containers:
      - name: app
        image: gcr.io/my-project/edge-sdk:latest
        env:
        - name: DB_MODE
          value: "direct"
        - name: DB_INSTANCE
          value: "my-project:us-central1:my-instance"
        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: database
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
      serviceAccountName: cloudsql-client
```

## Troubleshooting

### Cloud SQL Proxy Not Connecting

```bash
# Verify proxy is running
ps aux | grep cloud-sql-proxy

# Start proxy with verbose logging
cloud-sql-proxy my-project:us-central1:my-instance --verbose

# Test connection
psql "host=localhost port=5432 dbname=saastify_edge user=postgres"
```

### Permission Issues (Production)

Ensure the service account has the following IAM roles:
- `roles/cloudsql.client` - For Cloud SQL access
- `roles/cloudsql.instanceUser` - For database authentication

```bash
# Grant permissions
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:my-service@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

### Connection Pool Exhaustion

```bash
# Increase pool size
export DB_POOL_SIZE=20
export DB_MAX_OVERFLOW=40
```
