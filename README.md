# GangaCloud Customer Data Engineering Demo

This repository is a standalone, customer-facing demo for a private GangaCloud Data Engineering Workspace. It shows a small end-to-end PySpark ETL flow and a lightweight local Docker data stack without any control-plane integration.

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
|   `-- ssh-access.md
|-- jobs/
|   `-- orders_etl.py
|-- notebooks/
|   `-- orders_etl_notebook.md
|-- scripts/
|   `-- check_stack.sh
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
- Docker Engine with Docker Compose, required for the M28.3 stack

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

## Current Limitations

- Local PySpark mode only.
- Static sample CSV input.
- Parquet output is generated locally under `data/output/` and is not committed.
- M28.3 starts PostgreSQL and MinIO but does not yet load demo data into either service.
- No Airflow, Kubernetes, FastAPI, public Jupyter, multi-node Spark, provisioning automation, billing changes, product-plan changes, or GangaCloud control-plane integration in this milestone.

## M28.2 Milestone

M28.2 focuses on a clean customer demo of the private GangaCloud Data Engineering Workspace experience: read data, transform it with PySpark, persist Parquet, read it back, and validate the exact business result.

## M28.3 Milestone

M28.3 adds a local-only Docker data stack with PostgreSQL and MinIO for future customer workspace demos while keeping all service ports bound to localhost.
