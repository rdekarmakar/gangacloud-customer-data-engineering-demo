# End-to-End ETL Demo

M28.4 connects the existing local PySpark transformation to the private PostgreSQL and MinIO services introduced in M28.3. It remains a small, standalone customer demo with no GangaCloud control-plane integration.

## Architecture and Data Flow

```text
data/input/orders.csv
-> PySpark local-mode transformation
-> data/output/platform_etl/category_summary (Parquet)
-> MinIO: gangacloud-data/orders/curated/category_summary/category_summary.parquet
-> PostgreSQL: category_order_summary
-> independent MinIO and PostgreSQL validation
```

Spark reads the CSV, keeps successful orders, and aggregates count and amount by category. A regular S3-compatible Python client uploads the resulting Parquet file to MinIO, and psycopg loads the three aggregate rows into PostgreSQL.

## Prerequisites

- Python 3.10, 3.11, or 3.12
- Java available on `PATH`
- `make`
- Docker Engine with Docker Compose
- SSH access to the private workspace VM when running remotely

## Configure the Environment

Create the local environment file and replace both example passwords:

```bash
cp .env.example .env
```

The Python tools load PostgreSQL and MinIO settings from `.env`. The file is ignored by Git and must not be committed.

Install the pinned Python dependencies:

```bash
make setup
```

## Start and Check PostgreSQL and MinIO

```bash
make stack-up
make stack-check
```

Both services remain bound to `127.0.0.1` on the workspace VM.

## Initialize Storage

```bash
make storage-init
```

This idempotently creates the configured MinIO bucket and the PostgreSQL `category_order_summary` table. It does not delete existing data.

## Run and Validate the Pipeline

```bash
make pipeline-run
make pipeline-validate
```

After the one-time dependency setup, the complete safe workflow is also available as:

```bash
make demo
```

`make demo` starts the existing containers if necessary, checks them, initializes storage, runs the pipeline, and validates the result. It does not stop containers, remove volumes, or delete the MinIO bucket.

## Inspect PostgreSQL

From the workspace VM:

```bash
docker exec -it gc-de-postgres psql \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -c "SELECT * FROM category_order_summary ORDER BY category;"
```

If your shell has not loaded `.env`, supply the same database name and user configured there.

## Inspect MinIO

The expected object is:

```text
s3://gangacloud-data/orders/curated/category_summary/category_summary.parquet
```

To reach the private MinIO console from your local machine, create an SSH tunnel:

```bash
ssh -L 9001:127.0.0.1:9001 \
  -J rahul@<GANGACLOUD_PUBLIC_HOST> \
  ubuntu@10.10.0.103
```

Then open:

```text
http://127.0.0.1:9001
```

Sign in with `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from `.env`.

## Stop the Stack

```bash
make stack-down
```

This stops the containers while preserving their named volumes and data.

## Current Limitations

- Spark runs in local mode and writes one small Parquet part for the demo.
- PostgreSQL loading uses a deterministic delete-and-insert strategy.
- MinIO access uses `boto3`; Spark S3A and Hadoop AWS dependencies are intentionally absent.
- Spark does not connect to PostgreSQL through JDBC.
- No schema migrations, CDC, SCD, auditing framework, orchestration, or scheduling is included.
- No Airflow, Kubernetes, FastAPI, public services, multi-node Spark, provisioning automation, billing changes, product-plan changes, or control-plane integration is included.
