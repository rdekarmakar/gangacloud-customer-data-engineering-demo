#!/usr/bin/env bash
set -euo pipefail

status() {
  printf '\n==> %s\n' "$1"
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

status "Checking workspace prerequisites"
./scripts/check_prerequisites.sh

if [ ! -f requirements.txt ]; then
  echo "requirements.txt was not found in $repo_root."
  exit 1
fi

if [ ! -f .env.example ]; then
  echo ".env.example was not found in $repo_root."
  exit 1
fi

status "Preparing the Python virtual environment"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  echo "Created .venv."
elif [ ! -x .venv/bin/python ]; then
  echo ".venv exists but .venv/bin/python is unavailable."
  echo "Repair or remove the incomplete environment, then rerun this script."
  exit 1
else
  echo "Preserving the existing .venv."
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

status "Preparing local demo configuration"
if [ -e .env ]; then
  echo "Preserving the existing .env file."
else
  cp .env.example .env
  chmod 600 .env
  echo "Created .env from .env.example."
  echo "The file contains demo credentials. Change them for anything beyond this local/private demo."
fi

status "Starting PostgreSQL and MinIO"
make stack-up

status "Waiting for the Docker stack to become healthy"
stack_ready=0
for attempt in $(seq 1 18); do
  if make stack-check; then
    stack_ready=1
    break
  fi
  echo "Stack health check attempt $attempt of 18 was not ready; retrying in 5 seconds."
  sleep 5
done

if [ "$stack_ready" -ne 1 ]; then
  echo "PostgreSQL and MinIO did not become healthy within 90 seconds."
  echo "Inspect the services with: make stack-logs"
  exit 1
fi

status "Initializing MinIO and PostgreSQL storage"
make storage-init

status "Running the original PySpark validation"
make validate

status "Running the end-to-end pipeline"
make pipeline-run
make pipeline-validate

echo
echo "GangaCloud Data Engineering Workspace setup completed successfully."
