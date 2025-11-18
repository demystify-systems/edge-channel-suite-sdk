# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

The **Catalog Edge SDK** provides a unified framework for importing, transforming, validating and exporting product-related data across multiple channels (Amazon, Shopify, Flipkart, etc.) within the SaaStify ecosystem. The SDK is designed to process large files (200MB+), apply complex transformation pipelines via a DSL, validate data according to channel-specific templates, and produce ready-to-upload files or API payloads.

### Key Design Principles

- **Language Parity**: Both JavaScript/TypeScript and Python implementations share the same data model and transformation logic
- **Streaming Architecture**: Process large files row-by-row to avoid memory overload
- **Extensibility**: Transformation DSL and registry allow adding new operations without core engine changes
- **Completeness Cache**: Centralized cache (`product_template_completeness` table) stores intermediate transformed JSON, validation errors, and metadata for reuse during exports

## Repository Structure (Target)

This is a **monorepo** housing both JS/TS and Python SDKs:

```
edge-channel-suite-sdk/
├─ js-sdk/                    # JavaScript/TypeScript implementation
│   ├─ src/
│   │   ├─ import/           # Import pipeline orchestration
│   │   ├─ export/           # Export pipeline orchestration
│   │   ├─ core/             # Shared utilities (logging, config, file loaders)
│   │   ├─ validation/       # Validation engine and rules
│   │   ├─ transformations/  # Transformation operations registry
│   │   └─ index.ts
│   ├─ package.json
│   └─ tsconfig.json
├─ python-sdk/                # Python implementation
│   ├─ saastify_edge/
│   │   ├─ import/
│   │   ├─ export/
│   │   ├─ core/
│   │   ├─ validation/
│   │   ├─ transformations/
│   │   └─ __init__.py
│   ├─ pyproject.toml
│   └─ requirements.txt
├─ specs/                     # Shared specifications
│   ├─ transformation_registry.json
│   ├─ validation_rules.json
│   ├─ job_types.json
│   └─ schemas/
├─ scripts/                   # Utility scripts
└─ main_sdk.py               # Current Python prototype
```

## Current Implementation

The repository currently contains a **Python prototype** (`main_sdk.py`) implementing the core transformation DSL engine. This prototype demonstrates:

### Transformation DSL Architecture

The SDK uses a **pipeline-based transformation DSL** where operations are chained together using a pipe syntax:

```python
# Example: "uppercase + strip + replace|old|new"
bulk_apply_pipe_rules(
    values_list=["  hello world  ", "test data"],
    rule_strings="uppercase + strip + replace| |_"
)
# Result: ["HELLO_WORLD", "TEST_DATA"]
```

### Core Components in `main_sdk.py`

1. **RejectRow Exception**: Sentinel to mark rows for rejection during transformation
2. **Transform Helpers** (60+ functions): Individual transformation operations (uppercase, lowercase, split, join, replace, arithmetic, date manipulation, etc.)
3. **TRANSFORMS Registry**: Dictionary mapping operation names to functions
4. **apply_transformations()**: Executes a sequence of transformation steps on a value
5. **bulk_apply_pipe_rules()**: DSL interpreter supporting:
   - Broadcasting (single rule → many values or vice versa)
   - Pipe-delimited chains: `operation1 + operation2 + operation3`
   - Parameterized operations: `split|delimiter`, `replace|old|new`, `vlookup|key:val,key:val`

### Transformation Operations (Implemented)

**Text**: uppercase, lowercase, strip, title_case, capitalize, split, split_comma, join, replace, replace_regex, prefix, suffix, clean_html, clean_upc

**Numeric**: clean_numeric_value, addition, subtraction, multiplication, division, percentage, adjust_negative_to_zero, zero_padding

**Date**: date_only (converts datetime to date string)

**Control**: copy, rejects (marks row for rejection), set (sets constant value), set_number

**Lookup**: vlookup_map (dictionary-based value mapping)

### DSL Syntax Rules

- **Chaining**: Use ` + ` to chain operations (note spaces around `+`)
- **Parameters**: Use `|` separator: `operation|param1|param2`
- **Special delimiters**:
  - `split|||` or `split|\|` → split by pipe character `|`
  - `split|| ` or `split||` → split by space
  - `join|,` → join with comma
- **vlookup syntax**: `vlookup|key1:value1,key2:value2,...`
- **Arithmetic**: `addition|5`, `multiplication|2.5`, `division|10`

## Development Commands

### Python Development

Currently, the SDK is a single-file Python module. Testing requires creating a test script:

```bash
# Run the transformation engine
python3 main_sdk.py

# Test transformations interactively
python3 -c "
from main_sdk import bulk_apply_pipe_rules
result = bulk_apply_pipe_rules(['test value'], 'uppercase + strip')
print(result)
"
```

### Future Commands (Post-Structure)

```bash
# Python SDK
cd python-sdk
pip install -e .                    # Install in development mode
pytest tests/                       # Run tests
python -m saastify_edge.import      # Run import pipeline
python -m saastify_edge.export      # Run export pipeline

# JavaScript/TypeScript SDK
cd js-sdk
npm install
npm test                            # Run tests
npm run build                       # Compile TypeScript
npm run lint                        # Run linting
npm run typecheck                   # Type checking
```

## Key Architectural Concepts

### Import Pipeline Flow

1. **File Fetching**: HTTP/GCS/S3 sources → stream large files
2. **File Parsing**: Auto-detect format (CSV, TSV, XLSX, JSON, XML) → yield raw rows
3. **Template Mapping**: Retrieve channel template → map columns to SaaStify fields
4. **Transformation**: Apply pipeline from `transformations` array for each attribute
5. **Validation**: Apply rules from `validations` array → generate `validation_errors`
6. **Completeness Cache Write**: Store to `product_template_completeness` table with:
   - `transformed_response` (JSONB)
   - `validation_errors` (JSONB)
   - `is_valid`, `error_count`, `cache_freshness`
   - `run_type='IMPORT'`
7. **DB Write**: Upsert valid rows to product tables via GraphQL/SQL
8. **Job Status**: Update `saas_edge_jobs` with metrics per stage

### Export Pipeline Flow

1. **Entity Loading**: Fetch products from Postgres based on filters
2. **Cache Reuse**: Check `product_template_completeness` for fresh cached data
3. **Transformation**: Apply same pipelines as import (if cache miss)
4. **Validation**: Re-validate and update cache with `run_type='EXPORT'`
5. **File Building**: Generate CSV/XLSX/JSON/XML using `fileConfig` (delimiter, headers, sheet name)
6. **Upload**: Push to GCS/S3 or channel APIs
7. **Job Status**: Update metrics through export stages

### Transformation Context

When executing transformations, each operation receives:

- `value`: The current value being transformed
- `**kwargs`: Parameters from the pipeline step (e.g., `{"delimiter": ","}`)
- `context` (future): Full row data, template info, external lookup tables

This allows **cross-field operations** like:
```python
# Future capability
concat(fields=["brand", "name"], delimiter=" ")
coalesce(fields=["primary_title", "fallback_title"])
```

### Validation Engine

Validations are applied **after** transformations. Standard rules include:

- `required`: Value must be non-empty
- `regex`: Must match pattern
- `enum`: Must be in allowed values list
- `min_length`, `max_length`: String length constraints
- `numeric_range`: Number within min/max
- `date_before`, `date_after`: Date comparisons
- `custom_expression`: Row-level validation (e.g., `sale_price <= price`)

### Job Orchestration

Jobs tracked in `saas_edge_jobs` table with:

- **Import Stages**: IMPORT_FILE_FETCH, IMPORT_FILE_PARSE, IMPORT_TEMPLATE_MAP, IMPORT_TRANSFORM, IMPORT_VALIDATE, IMPORT_WRITE_CACHE, IMPORT_DB_WRITE, IMPORT_COMPLETE
- **Export Stages**: EXPORT_INIT, EXPORT_LOAD_TEMPLATE, EXPORT_FETCH_PRODUCTS, EXPORT_TRANSFORM, EXPORT_VALIDATE, EXPORT_WRITE_CACHE, EXPORT_BUILD_FILE, EXPORT_UPLOAD_FILE, EXPORT_NOTIFY
- **Metrics** (JSON): Timestamps, row counts, error counts, performance metrics per stage

## Working with Transformations

### Adding New Transformations

1. **Define the function** in the appropriate SDK:
   ```python
   def remove_emojis(v, **kw):
       """Remove all emoji characters from string."""
       import re
       emoji_pattern = re.compile("[...]")  # emoji regex
       return emoji_pattern.sub('', v) if isinstance(v, str) else v
   ```

2. **Register in TRANSFORMS dict**:
   ```python
   TRANSFORMS = {
       # ... existing ...
       "remove_emojis": remove_emojis
   }
   ```

3. **Update transformation_registry.json** in `specs/`:
   ```json
   {
     "id": "remove_emojis",
     "label": "Remove Emojis",
     "category": "text",
     "inputTypes": ["string"],
     "argSchema": {},
     "description": "Remove all emoji characters",
     "example": "Nice 😊 → Nice"
   }
   ```

4. **Implement in both JS and Python** to maintain parity

5. **Write tests** with golden fixtures to verify both implementations produce identical output

### Testing Transformations

Create test fixtures covering:
- Edge cases (null, empty string, special characters)
- Type variations (string, number, list)
- Parameter combinations
- Error handling (division by zero, invalid regex, etc.)

Example test structure:
```python
def test_uppercase():
    assert bulk_apply_pipe_rules(["hello"], "uppercase") == ["HELLO"]
    assert bulk_apply_pipe_rules([None], "uppercase") == [None]
    assert bulk_apply_pipe_rules([123], "uppercase") == [123]
```

## Integration Points

### Database Schema

**product_template_completeness** table:
- `internal_id` (uuid, PK)
- `job_id` (uuid, FK → saas_edge_jobs)
- `run_type` (IMPORT/EXPORT)
- `saas_edge_id` (uuid, tenant isolation)
- `product_id` (uuid, nullable)
- `template_id` (uuid)
- `transformed_response` (jsonb) — transformed field values
- `validation_errors` (jsonb) — errors keyed by attribute name
- `is_valid` (boolean)
- `error_count` (int)
- `cache_freshness` (boolean) — true if cache is current
- `processing_status` (text)
- `file_row_number` (int)
- `raw_input_snapshot` (jsonb)
- Timestamps: created_at, updated_at, last_product_updated_at, last_template_updated_at

Indexes:
- Unique: (saas_edge_id, template_id, product_id, job_id)
- Filter: (saas_edge_id, template_id, cache_freshness)

**saas_edge_jobs** table:
- `job_id` (uuid, PK)
- `job_type` (IMPORT/EXPORT)
- `job_status` (stage name)
- `request_args` (jsonb)
- `metrics` (jsonb) — stage timestamps, counts, errors
- `created_at`, `updated_at`

### GraphQL API

The SDK calls GraphQL endpoints for:
- Fetching channel templates and attribute definitions
- Loading product entities for export
- Upserting transformed products after import

Use structured queries to minimize round-trips and support batching.

### External Services

- **GCS/S3**: File upload/download via streaming
- **Channel APIs**: Amazon MWS, Shopify Admin API, Flipkart API
- **AI Services** (future): GPT-based enrichment for titles, descriptions

## Performance Considerations

### Streaming & Batching

- **Stream parsing**: Process files row-by-row using iterators/generators
- **Batch size**: Write to DB in batches of 500-1000 rows
- **Concurrency**: Use configurable worker pools (4-16 workers)
- **Backpressure**: Implement flow control to prevent memory overflow

### Target Throughput

- **50,000+ rows/minute** on Cloud Run (4 CPU, 4GB RAM)
- Handle files up to **200MB+** and **1M+ rows**

### Memory Management

- Avoid loading entire files into memory
- Use generators/async iterators
- Release resources after each batch
- Monitor memory usage and implement circuit breakers

## Code Quality Standards

### Type Safety

- **Python**: Use type hints everywhere; run `mypy` for static checking
- **TypeScript**: Strict mode enabled; no `any` types without explicit reason

### Error Handling

- Wrap I/O operations in try/catch with specific exception types
- Use exponential backoff for transient errors
- Never fail silently; log all errors with context (job_id, row_number, field_name)
- Distinguish between:
  - **Retryable errors**: Network, DB timeouts
  - **Fatal errors**: Invalid config, authentication failure
  - **Row errors**: Validation failures (continue processing)

### Testing Strategy

- **Unit tests**: Each transformation and validation rule
- **Integration tests**: Full import/export pipelines with mock DB
- **Parity tests**: Compare JS and Python output for identical inputs
- **Performance tests**: Benchmark with 100K+ row files

### Logging

Use structured logging with fields:
- `job_id`, `job_type`, `stage`, `row_number`, `template_id`, `saas_edge_id`
- Log levels: DEBUG (transformation details), INFO (stage transitions), WARN (validation errors), ERROR (failures)

## Multi-tenancy & Security

- **Tenant Isolation**: Filter all queries by `saas_edge_id`
- **Input Sanitization**: Strip HTML, remove scripts, validate file uploads
- **Secrets Management**: Use environment variables or cloud secret managers; never commit credentials
- **Audit Trail**: All operations recorded in job logs and completeness cache

## Migration Path

The current `main_sdk.py` is a **prototype**. To build the full SDK:

1. **Phase 1**: Establish monorepo structure with `js-sdk/` and `python-sdk/`
2. **Phase 2**: Port transformation engine from `main_sdk.py` to modular Python package
3. **Phase 3**: Implement JS/TS transformation engine with parity tests
4. **Phase 4**: Build import pipeline (file parsing → template mapping → DB write)
5. **Phase 5**: Build export pipeline (entity loading → cache reuse → file generation)
6. **Phase 6**: Add validation engine and completeness cache integration
7. **Phase 7**: Implement job orchestration and metrics collection
8. **Phase 8**: Create CLI tools and documentation

## Notes for Future Instances

- **Transformation parity is critical**: Any change to transformation logic must be implemented in both JS and Python with identical behavior
- **Registry is source of truth**: The `specs/transformation_registry.json` defines all available operations; UI and docs are generated from it
- **Cache freshness logic**: Check `last_product_updated_at` and `last_template_updated_at` before reusing cached transformations
- **Job metrics are append-only**: Each stage appends to the `metrics` JSON; never overwrite previous stages
- **Broadcasting rules**: Single rule + multiple values OR multiple rules + single value OR equal-length arrays
- **Pipe character escaping**: In DSL, use `|||` or `\|` to represent literal pipe delimiter in split operations
