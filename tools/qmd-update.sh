#!/usr/bin/env bash
# Refresh the project-local QMD index and verify its wiki collection.
set -euo pipefail

usage() {
  printf 'Usage: %s [--embed]\n' "${0##*/}" >&2
}

embed=false
case "$#" in
  0) ;;
  1)
    case "$1" in
      --embed) embed=true ;;
      -h|--help) usage; exit 0 ;;
      *) usage; exit 2 ;;
    esac
    ;;
  *) usage; exit 2 ;;
esac

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

if [[ ! -f .qmd/index.yml ]]; then
  printf 'Missing project-local QMD config: %s/.qmd/index.yml\n' "$root" >&2
  exit 1
fi

if ! command -v qmd >/dev/null 2>&1; then
  printf 'qmd is required; install @tobilu/qmd first.\n' >&2
  exit 127
fi

qmd update

if [[ "$embed" == true ]]; then
  qmd embed -c wiki
fi

qmd status
qmd collection show wiki
qmd ls wiki
qmd search -c wiki --json -n 5 "retrieval"
