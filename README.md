# S3-Native Decoupled Compute OLAP Query Engine

<div align="center">

# ⚡ S3-Native OLAP Engine

### Query raw CSV datasets directly from Amazon S3 using DuckDB, FastAPI, PostgreSQL, and a high-end React dashboard.

<br />

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge\&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi)
![DuckDB](https://img.shields.io/badge/DuckDB-OLAP-yellow?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Metadata-4169E1?style=for-the-badge\&logo=postgresql)
![Amazon S3](https://img.shields.io/badge/Amazon_S3-Object_Storage-569A31?style=for-the-badge\&logo=amazons3)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge\&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-UI-3178C6?style=for-the-badge\&logo=typescript)
![Vite](https://img.shields.io/badge/Vite-Build-646CFF?style=for-the-badge\&logo=vite)

<br />

**A cloud-native analytics engine that keeps data in S3 and brings compute to it on demand.**

<br />

[Live Demo](https://s3-native-decoupled-compute-olap-qu.vercel.app/) 
</div>

---

## Overview

**S3-Native Decoupled Compute OLAP Query Engine** is a portfolio-grade analytics platform that lets users upload CSV datasets to Amazon S3 and query them using SQL through DuckDB without loading the raw files into a traditional database.

The project demonstrates a modern data architecture pattern:

```text
Object Storage for raw durable data
+
On-demand compute for SQL execution
+
PostgreSQL metadata catalog
+
Professional browser-based analytics UI
```

The backend stores raw files in S3, keeps metadata in PostgreSQL, and uses DuckDB to execute SQL directly over S3-backed CSV files. The frontend provides a polished dashboard, dataset catalog, query console, and system overview.

---

## Live Deployment

| Layer             |             Service |              Status |
| ----------------- | ------------------: | ------------------: |
| Frontend          |              Vercel |            Deployed |
| Backend API       |              Render |            Deployed |
| Metadata Database | Supabase PostgreSQL |            Deployed |
| Object Storage    |           Amazon S3 |            Deployed |
| Query Engine      |              DuckDB | Embedded in backend |

> Replace the placeholder URLs with actual deployment links after deployment is completed.

```text
Frontend: https://YOUR_VERCEL_FRONTEND_URL
Backend:  https://YOUR_RENDER_BACKEND_URL
Docs:     https://YOUR_RENDER_BACKEND_URL/docs
```

---

## Product Preview

### Dashboard

A high-level system dashboard showing dataset volume, query activity, storage mode, uploaded data size, and recent query runs.

```text
Dashboard
├── Total datasets
├── Total rows
├── Total queries
├── Average execution time
├── Active storage backend
└── Latest query runs
```

### Datasets

A functional dataset catalog for uploading, inspecting, previewing, and downloading CSV files.

```text
Datasets
├── Upload CSV to S3
├── View registered datasets
├── Inspect schema metadata
├── Preview rows
└── Generate temporary download URL
```

### Query Console

An interactive SQL console for querying S3-backed datasets directly from the browser.

```text
Query Console
├── Select dataset
├── Write SQL
├── Execute query
├── View result table
├── Run EXPLAIN
└── Inspect recent query history
```

### System Overview

A safe runtime overview page that exposes operational information without leaking secrets.

```text
System
├── Backend status
├── API version
├── Environment
├── Storage backend
├── AWS region
├── S3 configuration status
├── Database configuration status
└── Catalog activity
```

---

## Architecture

```text
┌──────────────────────────────────────────────┐
│                 React Frontend               │
│        Dashboard · Datasets · SQL Console     │
└───────────────────────┬──────────────────────┘
                        │
                        │ HTTP API
                        ▼
┌──────────────────────────────────────────────┐
│                FastAPI Backend               │
│   Upload API · Query API · Dashboard API      │
└───────────────┬───────────────────┬──────────┘
                │                   │
                │ Metadata           │ Raw CSV Objects
                ▼                   ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│      PostgreSQL DB        │   │        Amazon S3          │
│ datasets · query_runs     │   │   datasets/*.csv          │
└──────────────────────────┘   └─────────────┬────────────┘
                                             │
                                             │ s3:// read
                                             ▼
                                ┌──────────────────────────┐
                                │          DuckDB           │
                                │   SQL over S3 CSV files   │
                                └──────────────────────────┘
```

---

## Core Data Flow

```text
1. User uploads CSV from the frontend
2. FastAPI receives the file
3. CSV analyzer extracts file size, row count, column count, and schema
4. Raw CSV is uploaded to private Amazon S3
5. Dataset metadata is stored in PostgreSQL
6. User selects a dataset in the Query Console
7. DuckDB reads the CSV directly from S3
8. SQL result is returned to the frontend
9. Query execution is recorded in PostgreSQL
```

---

## Why This Project Exists

Traditional analytics workflows often require data to be loaded into a database before it can be queried. This project explores a more cloud-native approach:

* Keep raw data in object storage
* Store only metadata in PostgreSQL
* Run SQL compute on demand
* Avoid duplicating raw files into a traditional database
* Provide a clean interface for querying, previewing, and observing analytics workloads

This mirrors simplified ideas from modern lakehouse and serverless analytics systems.

---

## Key Features

### S3-Native Dataset Storage

Raw CSV files are stored in a private S3 bucket under the `datasets/` prefix.

```text
s3://bucket-name/datasets/{uuid}-{filename}.csv
```

The backend uses a storage abstraction layer:

```text
ObjectStorage
├── LocalObjectStorage
└── S3ObjectStorage
```

This allows local development and cloud deployment without rewriting application logic.

---

### CSV Metadata Analyzer

Each uploaded CSV is analyzed before registration.

Captured metadata:

* File size
* Row count
* Column count
* Inferred schema
* Original filename
* Storage object key
* Upload status

---

### PostgreSQL Metadata Catalog

The system stores dataset metadata and query history in PostgreSQL.

Main tables:

```text
datasets
query_runs
```

The metadata catalog allows the frontend to list datasets, show schema summaries, track usage, and power dashboard metrics.

---

### DuckDB Query Engine

DuckDB executes SQL directly over S3-backed CSV files.

For v1, each selected dataset is exposed as a virtual table named:

```sql
dataset
```

Example:

```sql
SELECT *
FROM dataset
LIMIT 20;
```

Another example:

```sql
SELECT region, SUM(amount) AS total_amount
FROM dataset
GROUP BY region
ORDER BY total_amount DESC;
```

---

### Read-Only SQL Safety Layer

The backend accepts only read-style analytical queries.

Allowed starts:

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

This keeps the v1 demo focused on safe analytical query execution.

---

### EXPLAIN Plan Support

The Query Console can request DuckDB query plans through:

```text
POST /api/v1/queries/explain
```

This helps demonstrate database internals, physical query planning, and OLAP execution behavior.

---

### Presigned Download URLs

The backend can generate temporary S3 download URLs for raw dataset files.

```text
GET /api/v1/datasets/{dataset_id}/download-url
```

This avoids routing large file downloads through backend memory.

---

### Query Run History

Every successful query execution is persisted.

Tracked fields:

* Dataset ID
* SQL text
* Status
* Storage backend
* Row count
* Execution time
* Error message
* Timestamp

This powers dashboard observability and recent query history.

---

### Professional Frontend

The frontend is designed as a polished cloud-console-style analytics product.

Current sections:

```text
Dashboard
Datasets
Query Console
System
```

Design direction:

* Minimalist
* Dark interface
* High visual clarity
* Strong spacing
* Clean cards and tables
* Functional navigation
* Recruiter-friendly first impression

---

## API Overview

### Health

```http
GET /api/v1/health
```

### Dashboard

```http
GET /api/v1/dashboard/summary
```

### Datasets

```http
GET  /api/v1/datasets
POST /api/v1/datasets
POST /api/v1/datasets/upload
GET  /api/v1/datasets/{dataset_id}
GET  /api/v1/datasets/{dataset_id}/preview
GET  /api/v1/datasets/{dataset_id}/download-url
```

### Queries

```http
POST /api/v1/queries/execute
POST /api/v1/queries/explain
GET  /api/v1/queries/runs
```

### System

```http
GET /api/v1/system/overview
```

---

## Example Query Request

```json
{
  "dataset_id": "bee6ec58-33e4-4c29-b5b2-df20ffd2502e",
  "sql": "SELECT * FROM dataset LIMIT 20"
}
```

Example response:

```json
{
  "dataset_id": "bee6ec58-33e4-4c29-b5b2-df20ffd2502e",
  "sql": "SELECT * FROM dataset LIMIT 20",
  "columns": ["id", "amount", "region"],
  "rows": [
    {
      "id": 1,
      "amount": 100.5,
      "region": "North"
    }
  ],
  "row_count": 1,
  "execution_time_ms": 409.46
}
```

---

## Tech Stack

### Backend

| Area             | Technology     |
| ---------------- | -------------- |
| API              | FastAPI        |
| Language         | Python         |
| Query Engine     | DuckDB         |
| Metadata DB      | PostgreSQL     |
| ORM              | SQLAlchemy     |
| Migrations       | Alembic        |
| Object Storage   | Amazon S3      |
| AWS SDK          | boto3          |
| Package Manager  | uv             |
| Local DB Runtime | Docker Compose |

### Frontend

| Area       | Technology   |
| ---------- | ------------ |
| UI         | React        |
| Language   | TypeScript   |
| Build Tool | Vite         |
| Styling    | Tailwind CSS |
| Icons      | Lucide React |
| Deployment | Vercel       |

### Cloud

| Area              | Service             |
| ----------------- | ------------------- |
| Frontend Hosting  | Vercel              |
| Backend Hosting   | Render              |
| Metadata Database | Supabase PostgreSQL |
| Object Storage    | Amazon S3           |
| Region            | ap-south-1          |

---

## Local Development

### Prerequisites

* Python
* uv
* Node.js
* npm
* Docker Desktop
* AWS account
* S3 bucket
* IAM user or role with limited S3 access

---

### 1. Clone Repository

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

PostgreSQL runs locally on:

```text
localhost:5433
```

---

### 3. Configure Backend Environment

Create:

```text
backend/.env
```

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

AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key

ENVIRONMENT=development
DEBUG=true
```

Never commit `.env`.

---

### 4. Run Migrations

```bash
uv run alembic upgrade head
```

---

### 5. Start Backend

```bash
uv run python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

---

### 6. Start Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Deployment

### Frontend: Vercel

The frontend is deployed on Vercel.

Recommended environment variable:

```env
VITE_API_BASE_URL=https://YOUR_RENDER_BACKEND_URL
```

For local development, Vite proxies `/api` requests to the local backend.

---

### Backend: Render

The FastAPI backend is deployed on Render.

Recommended start command:

```bash
uv run python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```env
PROJECT_NAME=S3 Native Decoupled Compute OLAP Query Engine
API_VERSION=v1
DATABASE_URL=your-supabase-postgres-url
STORAGE_BACKEND=s3
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-private-s3-bucket
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
ENVIRONMENT=production
DEBUG=false
```

---

### Database: Supabase PostgreSQL

Supabase PostgreSQL is used as the production metadata database.

The backend stores:

```text
datasets
query_runs
```

Run migrations against the production database before using the deployed API.

---

### Storage: Amazon S3

Recommended S3 configuration:

* General purpose bucket
* Block Public Access enabled
* ACLs disabled
* Bucket owner enforced
* SSE-S3 encryption enabled
* Versioning disabled for development
* IAM access limited to the project bucket and `datasets/*`

---

## Security Notes

This project intentionally avoids exposing secrets to the frontend.

The System page does not expose:

```text
AWS access key
AWS secret key
Database password
Private S3 bucket name
Full database URL
```

The frontend only receives safe metadata such as:

```text
storage backend
environment
API version
region
configuration status
dataset count
query count
```

---

## Current Progress

### Completed

* FastAPI backend scaffold
* PostgreSQL persistence
* Alembic migrations
* Dataset catalog
* CSV metadata analyzer
* S3 object storage backend
* Storage abstraction layer
* DuckDB query engine
* DuckDB S3 reads
* Dataset preview endpoint
* Query execution endpoint
* EXPLAIN endpoint
* Presigned download URL endpoint
* Query run history
* Dashboard summary API
* System overview API
* Professional React dashboard
* Functional dataset catalog
* Browser-based CSV upload
* Dataset preview UI
* Dataset download action
* Interactive SQL query console
* EXPLAIN plan UI
* System overview UI
* Cloud deployment architecture

### Remaining Polish

* Benchmark suite
* Automated tests
* Final screenshots
* Architecture diagrams
* Production monitoring polish
* Measured performance claims

---

## Benchmark Plan

Benchmarking is planned as the next engineering phase.

Planned measurements:

* Query execution latency
* Upload memory behavior
* Backend memory usage during CSV upload
* DuckDB S3 scan performance
* Naive backend buffering vs object-storage upload
* S3-backed query flow vs database-loaded workflow

No final performance claims are made until benchmark data is collected.

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
├── benchmarks
├── samples
├── scripts
└── README.md
```

---

## Talking Points

This project demonstrates:

* Decoupled storage and compute architecture
* Object-storage-first analytics design
* SQL query execution over raw S3 files
* Metadata cataloging with PostgreSQL
* Query execution observability
* Presigned URL file access
* Secure S3 access patterns
* Full-stack product engineering
* Clean API design
* Cloud deployment planning
* Professional UI/UX execution

---

## Author

**Mayank Verma**

Computer Science & Engineering student focused on backend systems, cloud infrastructure, data engineering, and applied analytics platforms.

</div>
