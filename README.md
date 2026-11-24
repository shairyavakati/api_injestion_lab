# API-to-PostgreSQL Data Ingestion Pipeline

A Python-based data engineering project that extracts paginated data from a REST API, validates records, handles request failures, and loads data into PostgreSQL.

## Project Overview

This project demonstrates the fundamentals of building a reliable API ingestion pipeline.

A mock e-commerce API provides 1,000 order records across 10 pages. A Python ingestion client retrieves the records, validates data quality, and loads them into a PostgreSQL database.

The pipeline also implements retry handling and duplicate prevention to make repeated ingestion runs safer.

## Architecture

```text
Mock REST API
     |
     v
Python Ingestion Client
     |
     v
API Data Extraction
(Pagination & Retry Handling)
     |
     v
Data Validation
(Record Count & Unique IDs)
     |
     v
PostgreSQL Loader
     |
     v
PostgreSQL Database
```

## Tech Stack

- **Python** – Data extraction and processing
- **FastAPI** – Mock REST API
- **Requests** – HTTP communication
- **PostgreSQL** – Data storage
- **Psycopg2** – PostgreSQL connectivity
- **Python-dotenv** – Environment variable management
- **Logging** – Pipeline execution monitoring
- **Git & GitHub** – Version control

## Features

- REST API data extraction
- Paginated data ingestion
- HTTP 429 rate-limit handling
- Retry mechanism with exponential backoff
- Request timeout and connection error handling
- Data validation
- Unique order ID verification
- PostgreSQL database integration
- Duplicate prevention using `ON CONFLICT DO NOTHING`
- Transaction handling with commit and rollback
- Structured execution logs

## Project Structure

```text
api_injestion_lab/
│
├── api_server.py
├── ingestion_client.py
├── database.py
├── loader.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Database Schema

Table: `api_orders`

| Column | Data Type | Description |
|---|---|---|
| order_id | INTEGER | Unique order identifier |
| customer_name | VARCHAR | Customer name |
| amount | NUMERIC(10,2) | Order amount |
| ingested_at | TIMESTAMP | Record ingestion timestamp |

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/api_injestion_lab.git
cd api_injestion_lab
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=foundry_ai
DB_USER=postgres
DB_PASSWORD=your_password
```

Use your own PostgreSQL credentials. Never commit `.env` to GitHub.

### 5. Create the PostgreSQL table

Execute this SQL in PostgreSQL:

```sql
CREATE TABLE api_orders (
    order_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Start the mock API server

Open the first terminal:

```bash
python -m uvicorn api_server:app --host 127.0.0.1 --port 8001
```

Keep the server running.

### 7. Run the ingestion pipeline

Open a second terminal:

```bash
python ingestion_client.py
```

## Data Validation

The pipeline validates:

- Total records extracted.
- Number of unique order IDs.
- Successful retrieval of all API pages.

PostgreSQL record count can be verified using:

```sql
SELECT COUNT(*) FROM api_orders;
```

Inspect ingested records:

```sql
SELECT *
FROM api_orders
ORDER BY order_id
LIMIT 10;
```

## Expected Results

| Metric | Expected Result |
|---|---:|
| Total API records | 1,000 |
| Total pages | 10 |
| Records per page | 100 |
| Unique order IDs
