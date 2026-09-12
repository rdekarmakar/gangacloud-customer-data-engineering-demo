# GangaCloud Customer Data Engineering Demo

This repository is a standalone, customer-facing demo for a private GangaCloud Data Engineering Workspace. It shows a PySpark ETL flow backed by a lightweight, local-only PostgreSQL and MinIO data stack without any control-plane integration.

## ETL Flow

```text
data/input/orders.csv
-> PySpark reads CSV
-> filters successful orders
-> aggregates by category
-> writes Parquet
-> reads Parquet back
-> validates expected result
```

## Expected Output

| category | successful_order_count | total_success_amount |
| --- | ---: | ---: |
| ai | 1 | 1500 |
| cloud | 2 | 2000 |
| data | 3 | 4700 |

## Project Structure

```text
.
|-- data/
|   |-- input/
|   |   `-- orders.csv
|   `-- output/
|-- docs/
|   |-- docker-stack.md
|   |-- end-to-end-etl.md
|   `-- ssh-access.md
|-- jobs/
|   |-- orders_etl.py
|   `-- orders_platform_etl.py
|-- notebooks/
|   `-- orders_etl_notebook.md
|-- scripts/
|   |-- check_stack.sh
|   |-- init_storage.py
|   `-- validate_pipeline.py
|-- .env.example
|-- .gitattributes
|-- .gitignore
|-- docker-compose.yml
|-- Makefile
|-- README.md
`-- requirements.txt
```

## Prerequisites

- Python 3.10, 3.11, or 3.12 recommended for the pinned dependencies
- `make`
- Java available on `PATH`, required by PySpark
- Docker Engine with Docker Compose, required for the M28.3 and M28.4 stack

## Quick Start

```bash
make setup
make run
```

To run the validation flow explicitly:

```bash
make validate
```

Successful execution prints:

```text
Validation passed.
GangaCloud Data Engineering Workspace demo completed successfully.
```

## JupyterLab Usage

Install dependencies and start JupyterLab:

```bash
make setup
.venv/bin/jupyter lab
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\jupyter.exe lab
```

Use `notebooks/orders_etl_notebook.md` as the notebook-style walkthrough.

## SSH Access

SSH examples for the private workspace VM are documented in `docs/ssh-access.md`.

## M28.3 Docker Stack

M28.3 adds a lightweight local Docker Compose stack for PostgreSQL and MinIO on the workspace VM. Ports are bound to `127.0.0.1` only for safety.

```bash
cp .env.example .env
make stack-up
make stack-check
make stack-logs
make stack-down
```

See `docs/docker-stack.md` for setup, SSH tunnel examples, and reset instructions.

## M28.4 End-to-End Quick Start

M28.4 extends the local PySpark transformation through Parquet, MinIO, and PostgreSQL, then independently validates both external destinations.

```text
orders.csv -> PySpark -> Parquet -> MinIO -> PostgreSQL -> validation
```

Create `.env` and replace the example passwords before starting:

```bash
cp .env.example .env
make setup
make stack-up
make stack-check
make storage-init
make pipeline-run
make pipeline-validate
```

After `make setup`, the safe combined workflow is:

```bash
make demo
```

`make demo` starts and checks the stack, initializes storage, runs the pipeline, and validates it. It does not remove volumes or stop the services. See `docs/end-to-end-etl.md` for architecture, inspection commands, and the private MinIO console tunnel.

## Current Limitations

- Local PySpark mode only.
- Static sample CSV input.
- Parquet output is generated locally under `data/output/` and is not committed.
- The M28.4 load is a deterministic demo replacement, not an incremental data pipeline.
- Spark does not use S3A for MinIO or JDBC for PostgreSQL.
- No Airflow, Kubernetes, FastAPI, public Jupyter, multi-node Spark, provisioning automation, billing changes, product-plan changes, or GangaCloud control-plane integration is included.

## M28.2 Milestone

M28.2 focuses on a clean customer demo of the private GangaCloud Data Engineering Workspace experience: read data, transform it with PySpark, persist Parquet, read it back, and validate the exact business result.

## M28.3 Milestone

M28.3 adds a local-only Docker data stack with PostgreSQL and MinIO for future customer workspace demos while keeping all service ports bound to localhost.

## M28.4 Milestone

M28.4 turns the earlier pieces into one end-to-end demo: PySpark creates the category summary, `boto3` stores its Parquet artifact in MinIO, psycopg loads the exact aggregate into PostgreSQL, and an independent validator checks both destinations.
