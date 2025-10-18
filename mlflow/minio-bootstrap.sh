#!/usr/bin/env bash
set -euo pipefail
mc alias set local http://minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
mc mb -p local/mlflow || true   # 이미 있으면 통과
