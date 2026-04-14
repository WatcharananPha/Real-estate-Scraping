#!/usr/bin/env bash
set -euo pipefail
cd /home/kongla/Documents/GitHub/Real-estate-Scraping

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

mkdir -p logs

PYTHON=python3
# Prefer virtualenv python if available
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
fi

SCRIPT_PATH="$(dirname "$0")/run_notebooks.py"

if command -v xvfb-run >/dev/null 2>&1; then
  xvfb-run -s "-screen 0 1920x1080x24" "$PYTHON" "$SCRIPT_PATH" "$@"
else
  "$PYTHON" "$SCRIPT_PATH" "$@"
fi
