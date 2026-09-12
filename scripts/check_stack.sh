#!/usr/bin/env bash
set -euo pipefail

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
fi

POSTGRES_DB="${POSTGRES_DB:-gangacloud_demo}"
POSTGRES_USER="${POSTGRES_USER:-gangacloud}"

require_container_running() {
  local container_name="$1"
  local is_running

  is_running="$(docker inspect -f '{{.State.Running}}' "$container_name" 2>/dev/null || true)"
  if [ "$is_running" != "true" ]; then
    echo "Container $container_name is not running."
    exit 1
  fi
}

echo "Docker Compose containers:"
docker compose ps

require_container_running "gc-de-postgres"
require_container_running "gc-de-minio"

echo "Checking PostgreSQL readiness..."
docker exec gc-de-postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Checking MinIO health endpoint..."
if command -v curl >/dev/null 2>&1; then
  curl -fsS "http://127.0.0.1:9000/minio/health/live" >/dev/null
else
  echo "curl is not installed; skipping local MinIO HTTP health check."
fi

echo "GangaCloud Data Engineering Docker stack is healthy."
