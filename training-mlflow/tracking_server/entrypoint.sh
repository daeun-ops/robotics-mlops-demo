#!/usr/bin/env bash
set -euo pipefail
mkdir -p /mlflow
exec mlflow server \
  --backend-store-uri "${MLFLOW_BACKEND_STORE_URI:-/mlflow}" \
  --default-artifact-root "${MLFLOW_ARTIFACT_ROOT:-s3://mlflow/}" \
  --host 0.0.0.0 --port "${MLFLOW_PORT:-5000}"
