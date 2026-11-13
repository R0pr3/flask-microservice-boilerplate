#!/usr/bin/env bash
# monitor.sh — read-only operational snapshot for a Dockerized Flask host.
#
# Safe by design: it only inspects state and never changes containers,
# firewall rules or bans. Safe to run as a non-root user with sudo hints.
#
# Usage:
#   ./scripts/monitor.sh            # full snapshot
#   ./scripts/monitor.sh --no-color # plain output (logs, CI)
set -uo pipefail

NO_COLOR=0
if [[ "${1:-}" == "--help" ]]; then
  sed -n '2,10p' "$0"
  exit 0
fi
[[ "${1:-}" == "--no-color" ]] && NO_COLOR=1

if [[ "${NO_COLOR}" -eq 0 && -t 1 ]]; then
  BOLD="\033[1m"; CYAN="\033[36m"; GREEN="\033[32m"; RED="\033[31m"; RESET="\033[0m"
else
  BOLD=""; CYAN=""; GREEN=""; RED=""; RESET=""
fi

section() {
  printf '\n%s== %s ==%s\n' "${BOLD}${CYAN}" "$1" "${RESET}"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

printf '%s\n' "${BOLD}NOC OPERATIONS SNAPSHOT${RESET}  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

section "Host"
printf 'hostname: %s\n' "$(hostname 2>/dev/null || echo unknown)"
uptime 2>/dev/null || true

section "Disk"
df -h / 2>/dev/null | awk 'NR==1 || /\//'

section "Memory"
if have free; then
  free -m | awk 'NR==1 || /Mem|Swap/'
else
  printf 'free not available on this platform\n'
fi

section "Docker containers"
if have docker; then
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || {
    printf '%sdocker not reachable (permission or daemon down)%s\n' "${RED}" "${RESET}"
  }
else
  printf 'docker CLI not installed\n'
fi

section "Container resources"
if have docker; then
  docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' 2>/dev/null || true
fi

section "Firewall (UFW)"
if have ufw; then
  ufw status 2>/dev/null || printf 'ufw present but requires elevated privileges\n'
else
  printf 'ufw not installed\n'
fi

section "Fail2Ban"
if have fail2ban-client; then
  fail2ban-client status 2>/dev/null || printf 'fail2ban not reachable\n'
else
  printf 'fail2ban-client not installed\n'
fi

section "Recent application errors"
if have docker; then
  for container in $(docker ps --format '{{.Names}}' 2>/dev/null); do
    count=$(docker logs --since 15m "${container}" 2>&1 \
      | grep -Eic 'error|critical|traceback' || true)
    if [[ "${count}" -gt 0 ]]; then
      printf '%s%-32s %s matches in last 15m%s\n' "${RED}" "${container}" "${count}" "${RESET}"
    else
      printf '%s%-32s clean%s\n' "${GREEN}" "${container}" "${RESET}"
    fi
  done
fi

section "HTTP health probe"
if have curl; then
  code=$(curl -sk -o /dev/null -w '%{http_code}' https://localhost/api/v1/health || echo 000)
  printf 'GET https://localhost/api/v1/health -> %s\n' "${code}"
else
  printf 'curl not installed\n'
fi

printf '\nDone. Snapshot is read-only.\n'
