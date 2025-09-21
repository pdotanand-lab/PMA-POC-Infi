#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
