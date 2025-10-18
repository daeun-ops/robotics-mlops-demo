from __future__ import annotations
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

# 환경 (docker-compose에서 주d입됨)
MLFLOW_ENV = {
    "MLFLOW_TRACKING_URI": os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000"),
    "MLFLOW_S3_ENDPOINT_URL": os.environ.get("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000"),
    "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin"),
    "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin"),
}

default_args = {
    "owner": "robotics-mlops",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
  dag_id="robotics_retrain_pipeline",
  description="로보틱스 재학습 파이프라인: ingest -> preprocess -> validate -> train",
  schedule_interval="0 3 * * *",   # ← 매일 새벽 3시 재학습 
  start_date=datetime(2025, 1, 1),
  catchup=False,
  max_active_runs=1,               # ← 중복 실행 방지
  default_args={
      "owner": "robotics-mlops",
      "retries": 2, # ← 실패시 2회 재시도     
      "retry_delay": timedelta(minutes=5),
      "email": ["?@naver.com"],  # ← 실패 알림 이메일로 발성
     },
     tags=["robotics", "mlops"],
 ):

    def _ingest():
        # 실제로는 sensor dataa 수집/적재(S3) logic 위치
        import pathlib, json, random, time
        p = pathlib.Path("/tmp/robotics")
        p.mkdir(parents=True, exist_ok=True)
        data = [{"ts": i, "acc": random.random(), "gyro": random.random()} for i in range(1000)]
        (p / "sensor.json").write_text(json.dumps(data))
        time.sleep(1)

    def _preprocess():
        # 실제로는 feature engineering / split / normalization .....???e더있을수도
        import json, pathlib
        p = pathlib.Path("/tmp/robotics")
        raw = json.loads((p / "sensor.json").read_text())
        # 단순한...(?) feature (mean)
        acc_mean = sum(d["acc"] for d in raw) / len(raw)
        gyro_mean = sum(d["gyro"] for d in raw) / len(raw)
        (p / "features.json").write_text(json.dumps({"acc_mean": acc_mean, "gyro_mean": gyro_mean}))


     # ─────────────────────────────────────────────────────────
    # 품질ㄹ검증 (features.json) 최소 체크
    # ─────────────────────────────────────────────────────────
    def _validate():
        import json, pathlib
        p = pathlib.Path("/opt/airflow/shared/features.json")  # ← 공유 볼륨 경로(아래 compose에 마운트)
        data = json.loads(p.read_text())
        assert "acc_mean" in data and "gyro_mean" in data, "필수 키 누락"
        assert -1.0 <= data["acc_mean"] <= 2.0, "acc_mean 범위 이탈"
        assert -1.0 <= data["gyro_mean"] <= 2.0, "gyro_mean 범위 이탈"

    validate = PythonVirtualenvOperator(
        task_id="validate_features",
        python_callable=_validate,
        requirements=[""],
        system_site_packages=False,
   )

     
    def _train_and_log(run_name: str = "robotics_demo"):
        # venv 안에 필요한 패키지 설치 한다음에 실행
        import os
        import json
        import mlflow
        from sklearn.linear_model import LogisticRegression
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        import numpy as np
        import pathlib

        mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.environ["MLFLOW_S3_ENDPOINT_URL"]

        # dummy dataset (status 분류 가정)
        X, y = make_classification(n_samples=1000, n_features=4, n_informative=3, random_state=42)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

        # features (sensor 집계값을 hyperparameter에 집어넣어 데모데모)
        f = json.loads(pathlib.Path("/tmp/robotics/features.json").read_text())
        C = max(0.1, float(f["acc_mean"] + f["gyro_mean"]))  # 장난...은 아니고 테스트용 hyperparameter

        with mlflow.start_run(run_name=run_name):
            mlflow.log_params({"model": "logreg", "C": C, "solver": "lbfgs"})
            clf = LogisticRegression(C=C, solver="lbfgs", max_iter=1000)
            clf.fit(Xtr, ytr)
            pred = clf.predict(Xte)
            acc = accuracy_score(yte, pred)
            mlflow.log_metric("accuracy", float(acc))

            # 간단한 model artifactt 저장
            np.save("/tmp/model.npy", clf.coef_)
            mlflow.log_artifact("/tmp/model.npy", artifact_path="artifacts")

            # (해도되소안해도되구 -> model registry 쓸거면 mlflow.sklearn.log_model(...)
            # 여기선 최소 skeleton 유지

    ingest = PythonVirtualenvOperator(
        task_id="ingest",
        python_callable=_ingest,
        requirements=[""],
        system_site_packages=False,
        op_kwargs={"output_path": "/opt/airflow/shared/features.json"}
    )

    preprocess = PythonVirtualenvOperator(
        task_id="preprocess",
        python_callable=_preprocess,
        requirements=[""],
        system_site_packages=False,
    )

    train = PythonVirtualenvOperator(
        task_id="train_and_log",
        python_callable=_train_and_log,
        requirements=["mlflow==2.14.3", "scikit-learn==1.5.2", "numpy", "boto3"],
        system_site_packages=False,
        op_kwargs={"run_name": "robotics_demo"},
        env=MLFLOW_ENV,  # MLflow 연결 정보 주입
        op_kwargs={"run_name":"robotics_demo","input_path":"/opt/airflow/shared/features.json"},
     )

+    ingest >> preprocess >> validate >> train
