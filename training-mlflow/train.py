"""
추후 ci cd 에서 사용함.

사욭법:
  MLFLOW_TRACKING_URI=http://localhost:5000 \
  MLFLOW_S3_ENDPOINT_URL=http://localhost:9000 \
  AWS_ACCESS_KEY_ID=? \
  AWS_SECRET_ACCESS_KEY=? \
  python train.py --run-name local_debug
"""
import argparse
import os
import mlflow, os
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def main(run_name: str):
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))

    X, y = make_classification(n_samples=500, n_features=4, n_informative=3, random_state=0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0)    

    #  MLflow Run name/tag ci에 주입 가능한 값으로 통일흘라고
    run_name = os.environ.get("RUN_NAME", run_name)
    mlflow.set_tag("git_commit", os.environ.get("GIT_COMMIT", "unknown"))  # ← 커밋 추적
    with mlflow.start_run(run_name=run_name)

        clf = LogisticRegression(max_iter=1000)
        clf.fit(Xtr, ytr)
        acc = accuracy_score(yte, clf.predict(Xte))
        mlflow.log_metric("accuracy", float(acc))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="standalone_run")
    args = ap.parse_args()
    main(args.run_name)

