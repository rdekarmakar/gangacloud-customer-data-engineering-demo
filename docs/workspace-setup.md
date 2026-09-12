# Repeatable Workspace Setup

M28.5 provides a repeatable way to prepare a fresh Ubuntu VM for the standalone GangaCloud customer data-engineering demo. It installs only the local runtime prerequisites and then uses the repository's existing validation paths.

## Supported System

The supported target is Ubuntu 24.04 LTS. Recommended VM sizing is:

- 4 vCPU
- 8 GB RAM
- 80 GB disk

These values are practical recommendations for this demo, not a hard platform guarantee. The prerequisite check warns about smaller systems without failing solely because of resource sizing.

## Fresh-VM Workflow

Clone the standalone repository:

```bash
git clone https://github.com/rdekarmakar/gangacloud-customer-data-engineering-demo.git
cd gangacloud-customer-data-engineering-demo
```

On a truly fresh VM, the prerequisite check may report missing components. It is read-only and safe to run:

```bash
make prerequisites
```

Install the required Ubuntu packages:

```bash
sudo ./scripts/bootstrap_workspace.sh
```

The bootstrap uses Ubuntu packages, enables and starts Docker, and adds the invoking non-root user to the `docker` group when needed. If group membership changes, log out and reconnect before continuing; the current login session will not automatically receive the new membership.

After reconnecting, prepare and validate the repository:

```bash
make workspace-setup
```

## Existing-VM Workflow

For an existing Ubuntu 24.04 workspace, start with the read-only check:

```bash
make prerequisites
```

If every required runtime passes, skip the OS bootstrap and run:

```bash
make workspace-setup
```

Run the bootstrap only when required packages are missing or need to be repaired.

## Environment Configuration

`make workspace-setup` creates `.env` from `.env.example` only when `.env` does not already exist. Existing configuration is always preserved. The generated file contains local demo credentials and is ignored by Git; change the passwords before using the stack for anything beyond this private demo.

PostgreSQL, the MinIO API, and the MinIO console remain bound to `127.0.0.1`. No public listener is configured.

## Docker Services

The setup starts:

- PostgreSQL 16 on `127.0.0.1:5432`
- MinIO API on `127.0.0.1:9000`
- MinIO console on `127.0.0.1:9001`

Check or inspect them with:

```bash
make stack-check
make stack-logs
```

## Run the Demo

After workspace setup succeeds, rerun the complete M28.4 data flow at any time:

```bash
make demo
```

This starts the services if necessary, initializes storage, runs the PySpark pipeline, and validates MinIO and PostgreSQL. It does not remove volumes or stop services.

## Re-running Setup Safely

`make workspace-setup` is designed to be run again. It preserves `.venv`, preserves `.env`, reuses Docker volumes, installs the pinned Python requirements, safely recreates generated Parquet output, and reloads the deterministic demo result.

It does not prune Docker, remove containers or volumes, modify SSH settings, change firewall rules, upgrade the operating system, or reboot the VM.

## Troubleshooting

### Docker permission denied

If the bootstrap added your account to the `docker` group, log out of the VM and reconnect. Confirm access with:

```bash
docker info
```

Do not work around the problem by making the Docker socket world-writable.

### Java missing

Run the bootstrap on Ubuntu 24.04, or install `openjdk-17-jdk` from the configured Ubuntu repositories. Confirm with `java -version`.

### Docker Compose unavailable

The bootstrap first looks for `docker-compose-v2`, then the compatible Ubuntu `docker-compose-plugin` package. If neither is available, confirm the appropriate official Ubuntu repository component is enabled, run `sudo apt-get update`, and retry. The bootstrap never downloads a remote install script.

### PostgreSQL or MinIO unhealthy

Inspect container status and logs:

```bash
docker compose ps
make stack-logs
```

Confirm that `.env` contains the same credentials used when the Docker volumes were first created. Changing PostgreSQL or MinIO credentials in `.env` does not rewrite credentials already stored in existing volumes.

### Insufficient memory or disk

Resource warnings do not stop the prerequisite check, but Spark and Docker may become unreliable on constrained hosts. Free disk space or resize the VM when possible, then rerun `make prerequisites`.

## Safety Limitations

- This is a repeatable demo bootstrap, not a production-managed Spark platform.
- It does not provision VMs or automate Proxmox.
- It does not modify SSH daemon configuration or firewall rules.
- It does not run `apt upgrade`, `dist-upgrade`, Docker prune, volume removal, or an automatic reboot.
- It does not install Airflow, Kubernetes, FastAPI, or multi-node Spark.
- It does not add provisioning, billing, product-plan, or GangaCloud control-plane integration.
- Public access to PostgreSQL, MinIO, and Jupyter is not configured.
