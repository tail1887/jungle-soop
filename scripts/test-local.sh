#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "[test-local] .venv가 없어 bootstrap 실행"
  bash "$SCRIPT_DIR/bootstrap.sh"
fi

if [[ "$#" -eq 0 ]]; then
  .venv/bin/python -m pytest -q
else
  .venv/bin/python -m pytest "$@"
fi
