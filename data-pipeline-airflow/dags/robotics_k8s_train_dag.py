from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

with DAG(
    dag_id="robotics_k8s_train",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["robotics","mlops","k8s"],
):
    train = KubernetesPodOperator(
        task_id="train",
        name="train",
        namespace="?",                 # ← 배포 namespacr
        service_account_name="?",      # ← SA (restricted SCC 로)
        image="ghcr.io/?/?/robotics-train:latest",  # ← 학습용 이미지 암거나
        cmds=["python","/app/train.py"],
        env_vars={
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
            "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
            "AWS_ACCESS_KEY_ID": "?",
            "AWS_SECRET_ACCESS_KEY": "?",
        },
        is_delete_operator_pod=True,   # ← job 종료 시 pod 정리
    )
