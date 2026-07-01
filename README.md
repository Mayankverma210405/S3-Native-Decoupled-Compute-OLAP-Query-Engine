# S3-Native Decoupled Compute OLAP Query Engine

A portfolio-grade OLAP query engine that executes SQL directly over raw CSV datasets stored in Amazon S3, using DuckDB as the embedded compute engine, PostgreSQL for metadata, and a professional React dashboard for interaction and observability.

The project demonstrates a modern **decoupled storage and compute architecture**: dataset files stay in object storage, while compute is performed on demand without loading raw data into a traditional database.

---

## Current Status

**Backend core:** mostly complete
**Frontend foundation:** in progress
**Benchmark suite:** planned
**Deployment:** planned

Current working capabilities:

* Upload CSV datasets through API and UI
* Store raw dataset files in a private S3 bucket
* Analyze CSV metadata including row count, column count, file size, and inferred schema
* Persist dataset metadata in PostgreSQL
* Query S3-backed CSV files using DuckDB
* Preview dataset rows
* Generate temporary presigned download URLs
* Track query execution history
* Expose dashboard summary metrics
* Display a professional React dashboard and functional datasets page

---

## Architecture

```text
Browser UI
   ↓
React + Vite Frontend
   ↓
FastAPI Backend
   ↓
DuckDB Query Engine
   ↓
Amazon S3 CSV Files

FastAPI Backend
   ↓
PostgreSQL Metadata Database
```

### Storage and Compute Flow

```text
CSV Upload
   ↓
FastAPI receives file
   ↓
CSV analyzer extracts metadata
   ↓
Raw file is uploaded to private S3
   ↓
Metadata is stored in PostgreSQL
   ↓
DuckDB reads CSV directly from S3
   ↓
SQL result is returned to the user
   ↓
Query run is recorded for observability
```

---

## Tech Stack

### Backend

* Python
* FastAPI
* DuckDB
* PostgreSQL
* SQLAlchemy
* Alembic
* AWS S3
* boto3
* uv
* Docker Compose

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Lucide React icons

### Cloud and Infrastructure

* Amazon S3 for object storage
* IAM least-privilege access policy
* PostgreSQL local development through Docker
* Planned deployment: Render backend, Vercel frontend, Supabase PostgreSQL

---

## Core Features Implemented

### Dataset Upload

Datasets can be uploaded as CSV files. The backend stores the original file in S3 and records metadata in PostgreSQL.

Implemented endpoint:

```text
POST /api/v1/datasets/upload
```

Stored metadata includes:

* Dataset name
* Original filename
* S3 object key
* File size
* Row count
* Column count
* Inferred schema
* Query count
* Last query timestamp

---

### S3 Object Storage Abstraction

The project supports a storage abstraction layer with two implementations:

```text
LocalObjectStorage
S3ObjectStorage
```

This allows the backend to run locally using filesystem storage and switch to Amazon S3 using configuration.

Example configuration:

```env
STORAGE_BACKEND=s3
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-private-bucket-name
```

---

### DuckDB Query Execution Over S3

DuckDB reads CSV files directly from S3 through its S3/httpfs support.

Implemented endpoint:

```text
POST /api/v1/queries/execute
```

Example request:

```json
{
  "dataset_id": "dataset-uuid",
  "sql": "SELECT region, amount FROM dataset ORDER BY amount DESC"
}
```

For v1, every selected dataset is exposed inside DuckDB as a table named:

```text
dataset
```

Example SQL:

```sql
SELECT *
FROM dataset
LIMIT 10;
```

---

### Query Safety

The backend currently allows read-only SQL queries.

Allowed query starts:

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

This is a first-layer safety mechanism for the portfolio version. A deeper SQL sandbox can be added later.

---

### Dataset Preview

Datasets can be previewed without counting the preview as a full query execution.

Implemented endpoint:

```text
GET /api/v1/datasets/{dataset_id}/preview
```

---

### Query Explain

DuckDB query plans can be inspected through an EXPLAIN endpoint.

Implemented endpoint:

```text
POST /api/v1/queries/explain
```

This helps demonstrate query planning, physical execution, and interview-level understanding of database internals.

---

### Presigned Download URLs

The backend can generate temporary download URLs for raw dataset files stored in S3.

Implemented endpoint:

```text
GET /api/v1/datasets/{dataset_id}/download-url
```

This allows the frontend to download files directly from S3 without routing the file through backend memory.

---

### Query Run History

Every successful query execution is persisted in PostgreSQL.

Implemented endpoint:

```text
GET /api/v1/queries/runs
```

Tracked fields include:

* Dataset ID
* SQL text
* Status
* Storage backend
* Returned row count
* Execution time
* Error message
* Created timestamp

---

### Dashboard Summary API

The backend exposes a dashboard-ready metrics endpoint.

Implemented endpoint:

```text
GET /api/v1/dashboard/summary
```

The response includes:

* Total datasets
* Total rows
* Total uploaded bytes
* Total query executions
* Successful queries
* Failed queries
* Average execution time
* Active storage backend
* Latest query runs

---

## Frontend Progress

The frontend currently includes:

* Professional dark minimalist dashboard shell
* Dashboard metrics cards
* Latest query runs table
* Functional datasets page
* CSV upload from browser
* Dataset list
* Dataset preview
* Presigned download action
* Navigation shell for Dashboard, Datasets, Query Console, and System

Design direction:

* Minimalist
* High-end
* Easy to navigate
* Recruiter-friendly
* Functional rather than decorative
* Clear visual hierarchy
* Dark cloud-console-inspired interface

---

## API Overview

### Health

```text
GET /api/v1/health
```

### Datasets

```text
GET  /api/v1/datasets
POST /api/v1/datasets
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

### Dashboard

```text
GET /api/v1/dashboard/summary
```

---

## Local Development

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

PostgreSQL runs on:

```text
localhost:5433
```

---

### 3. Configure backend environment

Create `backend/.env` using `.env.example` as a reference.

Example local configuration:

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

AWS credentials should be configured locally and never committed.

---

### 4. Run migrations

```bash
uv run alembic upgrade head
```

---

### 5. Start backend

```bash
uv run python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

### 6. Start frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## AWS Setup Notes

The project uses a private S3 bucket with a least-privilege IAM policy.

Recommended S3 configuration:

* Block Public Access enabled
* ACLs disabled
* Bucket owner enforced
* Versioning disabled for development
* SSE-S3 encryption enabled
* Access limited to one bucket and the `datasets/*` prefix

The backend should use an IAM user or role with access only to the project bucket.

Never commit:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
.env
```

---

## Current Database Tables

### datasets

Stores dataset metadata.

Main fields:

* id
* name
* original_filename
* s3_key
* storage_format
* content_type
* file_size_bytes
* row_count
* column_count
* schema_json
* status
* query_count
* last_query_at
* created_at
* updated_at

### query_runs

Stores query execution history.

Main fields:

* id
* dataset_id
* sql_text
* status
* storage_backend
* row_count
* execution_time_ms
* error_message
* created_at

---

## Project Roadmap

### Completed

* Backend project scaffold
* PostgreSQL persistence layer
* Dataset catalog schema
* Dataset repository and service layer
* CSV metadata analyzer
* Local storage abstraction
* S3 storage backend
* S3 upload flow
* DuckDB S3 query support
* Dataset preview
* Query EXPLAIN
* Presigned download URLs
* Query run history
* Dashboard summary endpoint
* Professional dashboard UI
* Functional datasets UI

### In Progress

* Frontend application workflow
* Query console UI
* System overview page

### Planned

* Query Console page with SQL editor
* EXPLAIN plan viewer in frontend
* Failed query logging
* Dataset deletion flow
* Benchmark suite
* Architecture diagrams
* Deployment to Render and Vercel
* Supabase PostgreSQL migration
* Final README polish with measured benchmark results

---

## Benchmark Plan

Benchmarking is planned but not yet finalized.

Planned metrics:

* Backend memory usage during upload
* Query execution latency
* S3 read performance
* Data transfer behavior
* Comparison against naive backend file buffering
* Cost comparison against always-on database-style storage

No benchmark claims are treated as final until measured and documented.

---

## Why This Project Matters

Traditional database-backed analytics systems often require data to be loaded into a database before querying. This project explores a more cloud-native pattern:

```text
Object storage for durable raw data
+
On-demand compute for SQL execution
+
Metadata database for cataloging and observability
```

This mirrors real-world lakehouse and serverless analytics ideas in a simplified, recruiter-friendly engineering project.

---

## Author

Mayank Verma

Project repository:

```text
S3-Native-Decoupled-Compute-OLAP-Query-Engine
```
