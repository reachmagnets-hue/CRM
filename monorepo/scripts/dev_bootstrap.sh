#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
echo "Bootstrap complete. Run: (source .venv/bin/activate && make -C backend dev)"
