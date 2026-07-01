# S3-Native Decoupled Compute OLAP Query Engine

A cloud-native OLAP query engine that executes SQL directly over raw CSV datasets stored in Amazon S3, using DuckDB as the embedded compute layer, PostgreSQL as the metadata catalog, FastAPI as the backend API, and React as a professional analytics dashboard.

The project demonstrates a modern **decoupled storage and compute architecture** where raw data remains in object storage, metadata is tracked separately, and compute is performed on demand.

---

## Live Demo

**Frontend:** `YOUR_VERCEL_FRONTEND_URL`
**Backend API:** `YOUR_RENDER_BACKEND_URL`
**API Docs:** `YOUR_RENDER_BACKEND_URL/docs`

---

## Project Showcase

### Engineering Dashboard

![Dashboard](docs/assets/screenshots/dashboard.png)

The dashboard summarizes datasets, total rows, uploaded storage, query count, average execution latency, active storage backend, and recent query runs.

---

### Dataset Catalog

![Datasets Page](docs/assets/screenshots/datasets.png)

The dataset page allows users to upload CSV files, store them in S3, inspect metadata, preview rows, and generate temporary download URLs.

---

### Query Console

![Query Console](docs/assets/screenshots/query-console.png)

The query console allows users to select a dataset, run SQL against the virtual DuckDB table named `dataset`, view result rows, and inspect DuckDB EXPLAIN plans.

---

### System Overview

![System Overview](docs/assets/screenshots/system-overview.png)

The system page exposes safe runtime information such as environment, storage backend, AWS region, S3 configuration status, database configuration status, dataset count, and query run count.

---

### S3 Object Storage

![S3 Bucket](docs/assets/screenshots/s3-bucket.png)

Uploaded CSV datasets are stored as private S3 objects under the `datasets/` prefix.

---

## Problem Statement

Analytics systems often require data to be loaded into a database before users can run SQL queries. This creates extra ingestion steps, duplicate storage, backend memory pressure, and operational overhead.

This project explores a simpler cloud-native pattern:

```text
Raw CSV files in S3
        +
PostgreSQL metadata catalog
        +
DuckDB on-demand query execution
        +
React dashboard for interaction
```

The result is a lightweight OLAP engine that can upload, catalog, preview, query, and download raw S3-backed datasets without moving them into a traditional analytics database.

---

## Key Features

* Upload CSV datasets from the browser
* Store raw files in private Amazon S3
* Analyze CSV metadata automatically
* Track dataset metadata in PostgreSQL
* Query CSV files directly from S3 using DuckDB
* Preview dataset rows from the UI
* Generate presigned download URLs
* Execute read-only SQL from a browser-based query console
* View DuckDB EXPLAIN query plans
* Track query execution history
* Display dashboard-level operational metrics
* Show safe runtime system information
* Professional dark minimalist frontend interface
* Deployment-ready full-stack architecture

---

## Architecture

```text
Browser
  |
  v
React + TypeScript + Vite Frontend
  |
  v
FastAPI Backend
  |
  +------------------------+
  |                        |
  v                        v
DuckDB Query Engine     PostgreSQL Metadata Catalog
  |
  v
Amazon S3 Raw CSV Storage
```

---

## Data Flow

```text
CSV Upload
   |
   v
FastAPI receives file
   |
   v
CSV analyzer extracts row count, column count, file size, and schema
   |
   v
Raw file is uploaded to private S3
   |
   v
Dataset metadata is stored in PostgreSQL
   |
   v
DuckDB reads the CSV directly from S3
   |
   v
SQL result is returned to the frontend
   |
   v
Query run is recorded for observability
```

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Lucide React icons

### Backend

* Python
* FastAPI
* DuckDB
* SQLAlchemy
* Alembic
* boto3
* uv

### Database and Storage

* PostgreSQL
* Amazon S3

### Deployment

* Frontend: Vercel
* Backend: Render
* Database: Supabase PostgreSQL
* Object Storage: Amazon S3

---

## Implemented Modules

### Dataset Management

The dataset module supports CSV uploads, metadata extraction, S3 object storage, listing datasets, previewing rows, and generating download URLs.

Important endpoints:

```text
GET  /api/v1/datasets
POST /api/v1/datasets/upload
GET  /api/v1/datasets/{dataset_id}
GET  /api/v1/datasets/{dataset_id}/preview
GET  /api/v1/datasets/{dataset_id}/download-url
```

---

### Query Engine

The query engine uses DuckDB to execute SQL directly over the uploaded CSV file stored in S3.

For v1, each selected dataset is exposed inside DuckDB as a virtual table named:

```text
dataset
```

Example query:

```sql
SELECT *
FROM dataset
LIMIT 20;
```

Important endpoints:

```text
POST /api/v1/queries/execute
POST /api/v1/queries/explain
GET  /api/v1/queries/runs
```

---

### Dashboard Metrics

The dashboard endpoint provides high-level operational metrics for the frontend.

Endpoint:

```text
GET /api/v1/dashboard/summary
```

Returned metrics include:

* Total datasets
* Total rows
* Total uploaded bytes
* Total queries
* Successful queries
* Failed queries
* Average execution time
* Active storage backend
* Latest query runs

---

### System Overview

The system overview endpoint exposes safe runtime information without leaking secrets.

Endpoint:

```text
GET /api/v1/system/overview
```

It includes:

* Project name
* API version
* Environment
* Debug mode
* Backend status
* Storage backend
* AWS region
* S3 configuration status
* Database configuration status
* Dataset count
* Query run count

It intentionally does **not** expose:

* AWS access keys
* AWS secret keys
* Database passwords
* Private bucket names
* `.env` values

---

## Security Design

The project follows a least-exposure design for local and deployed environments.

Security measures include:

* Private S3 bucket
* S3 Block Public Access enabled
* IAM access limited to the project bucket and `datasets/*` prefix
* No AWS credentials committed to GitHub
* Environment variables used for secrets
* Presigned URLs for temporary dataset downloads
* Read-only SQL execution policy for query requests
* System API does not expose secrets or private infrastructure identifiers

---

## SQL Safety

The query engine currently allows read-only SQL operations.

Allowed query types:

```text
SELECT
WITH
```

Blocked operations include:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
COPY
ATTACH
INSTALL
LOAD
EXPORT
PRAGMA
SET
CALL
```

This keeps the portfolio version focused on analytical querying and prevents obvious destructive operations.

---

## Database Schema

### `datasets`

Stores metadata for uploaded datasets.

Key fields:

* `id`
* `name`
* `original_filename`
* `s3_key`
* `storage_format`
* `content_type`
* `file_size_bytes`
* `row_count`
* `column_count`
* `schema_json`
* `status`
* `query_count`
* `last_query_at`
* `created_at`
* `updated_at`

---

### `query_runs`

Stores query execution history.

Key fields:

* `id`
* `dataset_id`
* `sql_text`
* `status`
* `storage_backend`
* `row_count`
* `execution_time_ms`
* `error_message`
* `created_at`

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mayankverma210405/S3-Native-Decoupled-Compute-OLAP-Query-Engine.git
cd S3-Native-Decoupled-Compute-OLAP-Query-Engine
```

---

### 2. Start PostgreSQL

```bash
cd backend
docker compose up -d
```

Local PostgreSQL runs on:

```text
localhost:5433
```

---

### 3. Configure backend environment

Create `backend/.env` using `.env.example`.

Example:

```env
PROJECT_NAME=S3 Native Decoupled Compute OLAP Query Engine
API_VERSION=v1
LOG_LEVEL=INFO

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/olap_engine

STORAGE_BACKEND=s3
LOCAL_STORAGE_PATH=storage

AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-private-s3-bucket

ENVIRONMENT=development
DEBUG=true
```

AWS credentials should be configured locally and must never be committed.

---

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

---

### 5. Start backend

```bash
uv run python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

---

### 6. Start frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## Deployment Overview

The deployed architecture uses:

```text
Vercel          -> React frontend
Render          -> FastAPI backend
Supabase        -> PostgreSQL metadata database
Amazon S3       -> Raw CSV object storage
```

---

## Deployment Environment Variables

### Backend

Required backend environment variables:

```env
PROJECT_NAME=S3 Native Decoupled Compute OLAP Query Engine
API_VERSION=v1
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=your_supabase_postgresql_url

STORAGE_BACKEND=s3
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your_private_s3_bucket

AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

---

### Frontend

If the frontend uses a deployed backend URL directly, configure:

```env
VITE_API_BASE_URL=your_render_backend_url
```

If the project is using Vite proxy only for local development, production should use a configured API base URL.

---

## Deployment Checklist

### AWS S3

* Create private S3 bucket
* Disable public access
* Disable ACLs
* Enable default encryption
* Create IAM policy scoped to one bucket
* Limit access to `datasets/*`
* Store credentials only in backend environment variables

### Supabase PostgreSQL

* Create PostgreSQL project
* Copy connection string
* Set `DATABASE_URL` in backend environment
* Run Alembic migrations against production database

### Render Backend

* Create web service
* Connect GitHub repository
* Set root directory to `backend`
* Configure build/start commands
* Add backend environment variables
* Deploy FastAPI service
* Verify `/api/v1/health`
* Verify `/docs`

### Vercel Frontend

* Create Vercel project
* Set root directory to `frontend`
* Configure frontend environment variables
* Deploy React app
* Verify dashboard loads production backend data

---

## Production API Endpoints

### Health

```text
GET /api/v1/health
```

### Dashboard

```text
GET /api/v1/dashboard/summary
```

### Datasets

```text
GET  /api/v1/datasets
POST /api/v1/datasets/upload
GET  /api/v1/datasets/{dataset_id}
GET  /api/v1/datasets/{dataset_id}/preview
GET  /api/v1/datasets/{dataset_id}/download-url
```

### Queries

```text
POST /api/v1/queries/execute
POST /api/v1/queries/explain
GET  /api/v1/queries/runs
```

### System

```text
GET /api/v1/system/overview
```

---

## Project Screenshots

Recommended screenshot files:

```text
docs/assets/screenshots/dashboard.png
docs/assets/screenshots/datasets.png
docs/assets/screenshots/query-console.png
docs/assets/screenshots/system-overview.png
docs/assets/screenshots/s3-bucket.png
docs/assets/screenshots/api-docs.png
```

Recommended showcase order:

1. Dashboard
2. Datasets page
3. Query Console
4. EXPLAIN plan
5. System Overview
6. S3 bucket object storage
7. API docs

---

## Benchmarking

Benchmarking is planned as a dedicated phase.

Planned benchmark areas:

* Backend memory behavior during upload
* DuckDB query execution latency over S3
* Query performance across different CSV sizes
* S3 object read behavior
* Comparison against naive backend file buffering
* Metadata query latency from PostgreSQL
* End-to-end upload and query timing

Benchmark results will be added after measurement.

No unmeasured performance claims are treated as final.

---

## Repository Structure

```text
.
├── backend
│   ├── src
│   │   ├── api
│   │   ├── core
│   │   ├── database
│   │   ├── schemas
│   │   ├── services
│   │   └── storage
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   └── README.md
│
├── frontend
│   ├── src
│   │   ├── api
│   │   ├── components
│   │   ├── layouts
│   │   ├── pages
│   │   ├── services
│   │   └── types
│   ├── package.json
│   └── vite.config.ts
│
├── docs
│   └── assets
│       └── screenshots
│
├── benchmarks
├── samples
├── scripts
└── README.md
```

---

## Author

**Mayank Verma**

Project:

```text
S3-Native Decoupled Compute OLAP Query Engine
```
