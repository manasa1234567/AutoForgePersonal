#!/usr/bin/env bash
set -euo pipefail

python3 -m uvicorn app.main:app --reload --app-dir backend &
BACKEND_PID=$!
trap 'kill $BACKEND_PID' EXIT
npm start
