#!/usr/bin/env bash
set -euo pipefail

failures=0
warnings=0

pass() {
  printf 'PASS: %s\n' "$1"
}

warn() {
  printf 'WARN: %s\n' "$1"
  warnings=$((warnings + 1))
}

fail() {
  printf 'FAIL: %s\n' "$1"
  failures=$((failures + 1))
}

command_version() {
  local label="$1"
  local command_name="$2"
  shift 2

  if command -v "$command_name" >/dev/null 2>&1; then
    pass "$label: $("$@" 2>&1 | head -n 1)"
  else
    fail "$label is required but was not found on PATH."
  fi
}

echo "GangaCloud Data Engineering Workspace prerequisite check"
echo

if [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  os_name="${PRETTY_NAME:-${NAME:-unknown}}"
  echo "Operating system: $os_name"
  if [ "${ID:-}" = "ubuntu" ]; then
    pass "Ubuntu detected."
    if [ "${VERSION_ID:-}" = "24.04" ]; then
      pass "Ubuntu 24.04 is the supported target release."
    else
      warn "Ubuntu ${VERSION_ID:-unknown} detected; Ubuntu 24.04 is recommended."
    fi
  else
    warn "This host is not Ubuntu; Ubuntu 24.04 is the supported target."
  fi
else
  warn "Unable to read /etc/os-release."
fi

architecture="$(uname -m)"
pass "CPU architecture: $architecture"

cpu_count="$(getconf _NPROCESSORS_ONLN 2>/dev/null || printf '0')"
if [ "$cpu_count" -ge 4 ] 2>/dev/null; then
  pass "Available CPU count: $cpu_count vCPU."
else
  warn "Available CPU count: $cpu_count vCPU; at least 4 vCPU is recommended."
fi

if [ -r /proc/meminfo ]; then
  memory_kb="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
  memory_gb=$((memory_kb / 1024 / 1024))
  if [ "$memory_kb" -ge 8388608 ]; then
    pass "Total memory: approximately ${memory_gb} GB."
  else
    warn "Total memory: approximately ${memory_gb} GB; at least 8 GB is recommended."
  fi
else
  warn "Unable to determine total memory from /proc/meminfo."
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
disk_kb="$(df -Pk "$repo_root" | awk 'NR == 2 {print $4}')"
disk_gb=$((disk_kb / 1024 / 1024))
if [ "$disk_kb" -ge 41943040 ]; then
  pass "Available disk space: approximately ${disk_gb} GB."
else
  warn "Available disk space: approximately ${disk_gb} GB; at least 40 GB free is recommended."
fi

if command -v python3 >/dev/null 2>&1; then
  python_version="$(python3 --version 2>&1)"
  python_major="$(python3 -c 'import sys; print(sys.version_info.major)')"
  python_minor="$(python3 -c 'import sys; print(sys.version_info.minor)')"
  if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 10 ] && [ "$python_minor" -le 12 ]; then
    pass "Python runtime: $python_version."
  else
    warn "Python runtime: $python_version; Python 3.10 through 3.12 is preferred."
  fi
else
  fail "python3 is required but was not found on PATH."
fi

if command -v java >/dev/null 2>&1; then
  java_version="$(java -version 2>&1 | awk -F'"' 'NR == 1 {print $2}')"
  java_major="${java_version%%.*}"
  if [ "$java_major" = "17" ]; then
    pass "Java runtime: version $java_version."
  else
    warn "Java runtime: version ${java_version:-unknown}; Java 17 is recommended."
  fi
else
  fail "java is required but was not found on PATH."
fi

command_version "Git" "git" git --version
command_version "Make" "make" make --version

if command -v docker >/dev/null 2>&1; then
  pass "Docker CLI: $(docker --version 2>&1)"
  if docker compose version >/dev/null 2>&1; then
    pass "Docker Compose: $(docker compose version 2>&1)"
  else
    fail "Docker Compose v2 is required but 'docker compose' is unavailable."
  fi

  if docker info >/dev/null 2>&1; then
    pass "Docker daemon is accessible to the current user."
  else
    fail "Docker daemon is not accessible to the current user. Start Docker or reconnect after joining the docker group."
  fi
else
  fail "docker is required but was not found on PATH."
  fail "Docker Compose v2 cannot be checked because Docker is missing."
fi

echo
if [ "$failures" -gt 0 ]; then
  echo "GangaCloud prerequisite check failed: $failures required check(s) failed and $warnings warning(s) were reported."
  echo "Install or fix the failed runtime components, then run this check again."
  exit 1
fi

if [ "$warnings" -gt 0 ]; then
  echo "Prerequisite recommendations: $warnings warning(s) reported."
fi
echo "GangaCloud Data Engineering Workspace prerequisite check passed."
