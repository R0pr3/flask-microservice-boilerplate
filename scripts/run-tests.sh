#!/usr/bin/env bash
# run-tests.sh — run the pytest suite inside the local virtualenv.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

"${PYTHON}" -m pytest "$@"
