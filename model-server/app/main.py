# --- MLflow 레지스트리에서 모델 로드 (Production) ---
import os
import mlflow
from fastapi import FastAPI
from prometheus_client import Histogram, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI()
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_URI = os.getenv("MODEL_URI", "models:/robotics-model/Production")  # 프로덕션 스테이지
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
model = mlflow.pyfunc.load_model(MODEL_URI)  # 스타트업에 최신 Prod 로드

# ── 메트릭 (간단 예시)
REQUESTS = Counter("inference_requests_total", "총 예측 요청 수")
FAILURES = Counter("inference_failure_total", "실패 수")
LAT_HIST = Histogram("inference_duration_seconds", "추론 지연(초)")
CONF_BUCKET = Histogram("inference_confidence_bucket", "확신도 히스토그램", buckets=[0.1*i for i in range(11)])
INPUT_KL = Gauge("input_kl_divergence", "입력 분포 KL-Divergence(베이스라인 대비)")

BASE_MEAN = float(os.getenv("BASE_MEAN", "0.0"))
BASE_STD = float(os.getenv("BASE_STD", "1.0"))

@app.get("/health")
def health():
    return {"ok": True, "model_uri": MODEL_URI}

@app.post("/predict")
def predict(payload: dict):
    import time, math, numpy as np
    start = time.time()
    try:
        x = payload.get("features")  # [a,b,c,d] 형태
        y = model.predict([x])[0]
        prob = float(y if isinstance(y, (int,float)) else y[0])
        REQUESTS.inc()
        CONF_BUCKET.observe(prob)

        # 아주 단순한 입력 드리프트(KL) 추정: 가우시안 가정
        arr = np.array(x, dtype=float)
        mu = arr.mean()
        sigma = arr.std() if arr.std() > 1e-6 else 1e-6
        # KL(N(mu,sigma^2)||N(BASE_MEAN,BASE_STD^2))
        kl = math.log(BASE_STD/sigma) + (sigma**2 + (mu-BASE_MEAN)**2)/(2*BASE_STD**2) - 0.5
        INPUT_KL.set(kl)

        return {"probability": prob}
    except Exception as e:
        FAILURES.inc()
        return {"error": str(e)}, 500
    finally:
        LAT_HIST.observe(time.time() - start)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


from .ml_inference import router as ml_router
app.include_router(ml_router)






