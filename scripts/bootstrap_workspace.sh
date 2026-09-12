#!/usr/bin/env bash
set -euo pipefail

status() {
  printf '\n==> %s\n' "$1"
}

if [ "${EUID}" -ne 0 ]; then
  echo "This bootstrap installs system packages and must run as root."
  echo "Run: sudo ./scripts/bootstrap_workspace.sh"
  exit 1
fi

if [ ! -r /etc/os-release ]; then
  echo "Unable to identify the operating system from /etc/os-release."
  exit 1
fi

# shellcheck disable=SC1091
. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then
  echo "Unsupported operating system: ${PRETTY_NAME:-unknown}. Ubuntu 24.04 is required."
  exit 1
fi

if [ "${VERSION_ID:-}" != "24.04" ]; then
  echo "WARNING: Ubuntu ${VERSION_ID:-unknown} detected; Ubuntu 24.04 is the supported target."
fi

status "Refreshing Ubuntu package metadata"
export DEBIAN_FRONTEND=noninteractive
apt-get update

compose_package=""
for candidate in docker-compose-v2 docker-compose-plugin; do
  if apt-cache show "$candidate" >/dev/null 2>&1; then
    compose_package="$candidate"
    break
  fi
done

if [ -z "$compose_package" ]; then
  echo "Docker Compose v2 is not available from the configured Ubuntu repositories."
  echo "Enable the appropriate official Ubuntu repository component, run apt-get update, and retry."
  echo "No remote installation script has been run."
  exit 1
fi

status "Installing workspace runtime packages"
apt-get install -y --no-install-recommends \
  git \
  make \
  curl \
  ca-certificates \
  python3 \
  python3-venv \
  python3-pip \
  openjdk-17-jdk \
  docker.io \
  "$compose_package"

status "Enabling and starting Docker"
systemctl enable docker
systemctl start docker

if ! docker info >/dev/null 2>&1; then
  echo "Docker was installed but the daemon is not responding."
  echo "Inspect it with: systemctl status docker"
  exit 1
fi

docker_group_changed=0
target_user="${SUDO_USER:-}"
if [ -n "$target_user" ] && [ "$target_user" != "root" ]; then
  if id -nG "$target_user" | grep -qw docker; then
    echo "User $target_user is already a member of the docker group."
  else
    status "Adding $target_user to the docker group"
    usermod -aG docker "$target_user"
    docker_group_changed=1
  fi
else
  echo "No non-root sudo user was detected; Docker group membership was not changed."
fi

status "Verifying installed runtimes"
python3 --version
java -version
git --version
make --version
docker --version
docker compose version

echo
echo "GangaCloud Data Engineering Workspace bootstrap completed successfully."
if [ "$docker_group_changed" -eq 1 ]; then
  echo "Docker group membership was updated for $target_user."
  echo "Log out and log back in before running make prerequisites or make workspace-setup."
fi
