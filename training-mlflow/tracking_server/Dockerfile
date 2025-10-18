FROM python:3.11-slim

RUN pip install --no-cache-dir mlflow boto3 gunicorn

# mlflow backend store (file) at /mlflow, artifacts -> MinIO (S3)
ENV MLFLOW_BACKEND_STORE_URI=/mlflow
ENV MLFLOW_ARTIFACT_ROOT=s3://mlflow/

WORKDIR /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
