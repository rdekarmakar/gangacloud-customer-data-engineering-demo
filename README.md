# GangaCloud Customer Data Engineering Demo

This repository is a standalone, customer-facing M28.2 demo for a private GangaCloud Data Engineering Workspace. It shows a small end-to-end PySpark ETL flow that runs locally inside this repo without any control-plane integration.

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
├── data/
│   ├── input/
│   │   └── orders.csv
│   └── output/
├── docs/
│   └── ssh-access.md
├── jobs/
│   └── orders_etl.py
├── notebooks/
│   └── orders_etl_notebook.md
├── Makefile
├── README.md
├── requirements.txt
└── .gitignore
```

## Prerequisites

- Python 3.10, 3.11, or 3.12 recommended for the pinned dependencies
- `make`
- Java available on `PATH`, required by PySpark

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

## Current Limitations

- Local PySpark mode only.
- Static sample CSV input.
- Parquet output is generated locally under `data/output/` and is not committed.
- No Docker, MinIO, PostgreSQL, Airflow, Kubernetes, FastAPI, or GangaCloud control-plane integration in this milestone.

## M28.2 Milestone

M28.2 focuses on a clean customer demo of the private GangaCloud Data Engineering Workspace experience: read data, transform it with PySpark, persist Parquet, read it back, and validate the exact business result.
