# Airflow Orchestration Demo

This optional M28.6 layer uses Apache Airflow to orchestrate the existing GangaCloud orders pipeline. Airflow remains in a separate Compose file, so the normal `make demo` workflow and the PostgreSQL/MinIO stack continue to operate independently.

## Architecture

```text
Airflow
-> PySpark transformation
-> Parquet output
-> MinIO object and PostgreSQL summary
-> independent pipeline validation
```

The manually triggered DAG runs two tasks in order:

1. `run_orders_platform_etl`
2. `validate_pipeline`

PostgreSQL and MinIO are resolved from the Airflow container by their Docker service names, `postgres` and `minio`. Their host ports remain bound to `127.0.0.1` by the existing stack.

## Build and Start

Create `.env` from the example if it does not already exist, and change the demo passwords when appropriate:

```bash
cp .env.example .env
```

Start and check the existing data services first:

```bash
make stack-up
make stack-check
make storage-init
```

Build and start only the Airflow service:

```bash
docker compose -f docker-compose.airflow.yml build airflow
docker compose -f docker-compose.airflow.yml up -d airflow
```

Inspect startup status and logs with:

```bash
docker compose -f docker-compose.airflow.yml ps
docker compose -f docker-compose.airflow.yml logs --tail=100 airflow
```

## Open the Private Airflow UI

Airflow binds only to `127.0.0.1:8080` on the workspace VM. From the customer machine, create an SSH tunnel through the jump host:

```bash
ssh -N -L 8080:127.0.0.1:8080 -J <jump-user>@<jump-host> ubuntu@<workspace-private-ip>
```

Open this local URL:

```text
http://localhost:8080
```

Use the credentials reported by the Airflow standalone startup process, open the `gangacloud_orders_pipeline` DAG, and trigger it manually. A successful run shows both `run_orders_platform_etl` and `validate_pipeline` in the successful state.

## Temporary Spark Output

The Airflow service sets:

```text
PIPELINE_OUTPUT_PATH=/tmp/gangacloud/platform_etl/category_summary
```

This container-local temporary path prevents Airflow execution from conflicting with normal workspace runs, which continue to write under `data/output/platform_etl/category_summary`.

## Stop Airflow

Stop the Airflow service without affecting PostgreSQL or MinIO:

```bash
docker compose -f docker-compose.airflow.yml down
```

This command preserves the named Airflow volumes. It does not remove the existing data-stack containers or volumes.

## Scope and Limitations

- The DAG is manually scheduled and uses Airflow's `LocalExecutor`.
- Spark remains local-mode inside the Airflow container.
- Airflow is an optional orchestration demo, not a production-managed service.
- The UI is not publicly exposed.
- No Kubernetes, multi-node Spark, provisioning automation, billing integration, or control-plane integration is included.
