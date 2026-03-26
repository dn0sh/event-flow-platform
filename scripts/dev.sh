#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=.
uvicorn src.api.main:app --host 0.0.0.0 --port 8060 --reload
