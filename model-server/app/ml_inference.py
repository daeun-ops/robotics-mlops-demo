# model-server/app/ml_inference.py
# MLflow Production 모델 로드 + /predict, /metrics + 기본 드리프트 지표
import os, time, math, json
import numpy as np
import mlflow
from fastapi import APIRouter, HTTPException
from prometheus_client import Histogram, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

router = APIRouter()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_URI = os.getenv("MODEL_URI", "models:/robotics-model/Production")
BASE_MEAN = float(os.getenv("BASE_MEAN", "0.0"))
BASE_STD  = float(os.getenv("BASE_STD",  "1.0"))

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
_model = mlflow.pyfunc.load_model(MODEL_URI)

REQUESTS   = Counter("inference_requests_total", "총 예측 요청 수")
FAILURES   = Counter("inference_failure_total", "실패 수")
LATENCY    = Histogram("inference_duration_seconds", "추론 지연(초)")
CONF_HIST  = Histogram("inference_confidence_bucket", "확신도 분포", buckets=[0.1*i for i in range(11)])
INPUT_KL   = Gauge("input_kl_divergence", "입력 분포 KL(N(mu,sigma)||N(BASE_MEAN,BASE_STD))")

@router.get("/health")
def health():
    return {"ok": True, "model_uri": MODEL_URI}

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.post("/predict")
def predict(payload: dict):
    start = time.time()
    try:
        x = payload.get("features")
        if x is None:
            raise ValueError("payload.features 가 필요합니다.")
        y = _model.predict([x])[0]
        # 확률형 모델이 아니라면 y를 float로 캐스팅
        prob = float(y if isinstance(y, (int, float)) else y[0])

        REQUESTS.inc()
        CONF_HIST.observe(prob)

        arr = np.array(x, dtype=float)
        mu  = arr.mean()
        sd  = arr.std() if arr.std() > 1e-6 else 1e-6
        # KL(N(mu,sd)||N(BASE_MEAN,BASE_STD))
        kl = math.log(BASE_STD/sd) + (sd**2 + (mu-BASE_MEAN)**2)/(2*BASE_STD**2) - 0.5
        INPUT_KL.set(kl)

        return {"probability": prob}
    except Exception as e:
        FAILURES.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        LATENCY.observe(time.time() - start)
