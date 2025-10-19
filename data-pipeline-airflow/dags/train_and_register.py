"""
학습 → MLflow에 등록(모델명 'robotics-model') → GitHub Actions repository_dispatch 트리거
필요 환경:
- AIRFLOW_VAR_GITHUB_OWNER, AIRFLOW_VAR_GITHUB_REPO
- AIRFLOW_VAR_GH_TOKEN (repo:dispatch 권한 PAT or Fine-grained)
- MLFLOW_TRACKING_URI
"""
import os, json, requests, mlflow, mlflow.sklearn
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

OWNER = os.getenv("AIRFLOW_VAR_GITHUB_OWNER", "?")
REPO  = os.getenv("AIRFLOW_VAR_GITHUB_REPO",  "?")
TOKEN = os.getenv("AIRFLOW_VAR_GH_TOKEN",      "?")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI","http://mlflow:5000")

def _train_and_register():
    import numpy as np
    X, y = make_classification(n_samples=2000, n_features=4, n_informative=3, random_state=42)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    with mlflow.start_run() as run:
        model = LogisticRegression()
        model.fit(Xtr, ytr)
        acc = model.score(Xte, yte)
        mlflow.log_metric("acc", float(acc))
        mlflow.sklearn.log_model(model, artifact_path="model")
        res = mlflow.register_model(f"runs:/{run.info.run_id}/model", "robotics-model")
        # Staging → 수동검증 후 Production 승격은 MLflow UI or 별도 스텝에서 처리 가능
        # 여기서는 데모로 바로 스테이징으로 둔다.
        print("registered version:", res.version)

    # GitHub Actions repository_dispatch 트리거 (모델 등록 알림)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/dispatches"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept":"application/vnd.github+json"}
    payload = {"event_type":"model-registered","client_payload":{"version": str(res.version)}}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    r.raise_for_status()

with DAG(
    dag_id="train_and_register",
    start_date=datetime(2025,1,1),
    schedule_interval="@daily",
    catchup=False,
    tags=["mlops","mlflow","auto-deploy"],
):
    PythonOperator(task_id="train_register_dispatch", python_callable=_train_and_register)
