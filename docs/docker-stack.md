# Docker Data Engineering Stack

M28.3 adds a lightweight Docker Compose stack for the standalone GangaCloud customer Data Engineering Workspace demo. It starts PostgreSQL and MinIO locally on the workspace VM so future milestones can demonstrate loading warehouse-style data and object storage artifacts.

This milestone does not yet load data into PostgreSQL or MinIO.

## Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and replace the example passwords before starting the stack:

```dotenv
POSTGRES_DB=gangacloud_demo
POSTGRES_USER=gangacloud
POSTGRES_PASSWORD=change-me-postgres-password
MINIO_ROOT_USER=gangacloud
MINIO_ROOT_PASSWORD=change-me-minio-password
```

Do not commit `.env`.

## Start the Stack

```bash
make stack-up
```

Equivalent Docker Compose command:

```bash
docker compose up -d
```

## Check Containers

```bash
docker compose ps
make stack-check
```

The health check script verifies that the PostgreSQL and MinIO containers are running and attempts basic local readiness checks.

Successful output ends with:

```text
GangaCloud Data Engineering Docker stack is healthy.
```

## View Logs

```bash
make stack-logs
```

Equivalent Docker Compose command:

```bash
docker compose logs --tail=100
```

## Stop the Stack

```bash
make stack-down
```

Equivalent Docker Compose command:

```bash
docker compose down
```

## Clean Reset

Only remove volumes when you intentionally want to delete local PostgreSQL and MinIO data:

```bash
docker compose down -v
```

The Makefile does not run destructive volume removal automatically.

## MinIO Console Through an SSH Tunnel

The MinIO API and console are bound to localhost on the workspace VM:

- API: `127.0.0.1:9000`
- Console: `127.0.0.1:9001`

From your local machine, create an SSH tunnel through the bastion:

```bash
ssh -L 9001:127.0.0.1:9001 -J ubuntu@bastion.example.com ubuntu@10.10.0.103
```

Then open the MinIO console locally:

```text
http://127.0.0.1:9001
```

Use `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from `.env`.

## Why Ports Bind to 127.0.0.1

PostgreSQL and MinIO are bound to `127.0.0.1` so they are reachable only from the workspace VM itself or through an explicit SSH tunnel. This avoids exposing demo credentials or internal services on the VM network interface.

## Limitations

- PostgreSQL and MinIO start as empty local services.
- No data is loaded into PostgreSQL or MinIO in M28.3.
- No Airflow, Kubernetes, FastAPI, public Jupyter, multi-node Spark, provisioning automation, billing changes, product-plan changes, or control-plane integration is included.
