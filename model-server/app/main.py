"""
Fast api 기반의 robotics model serving API
- /health: healthCheck~
- /predict: 예측수행
"""
from fastapi import FastAPI, HTTPException
import os, logging
from pydantic import BaseModel
from app.inference import predict
from app import drift
drift.start()
import time
from app.metrics import (
    REQUESTS_TOTAL, SUCCESS_TOTAL, FAIL_TOTAL, DURATION,
    LOWCONF_TOTAL, CONFIDENCE_HIST, INPUT_FPS, DRIFT_KL, QUEUE_BACKLOG
)
from logging_filter import MaskFilter
logger.addFilter(MaskFilter())

logging.basicConfig(level=logging.INFO)         # ← 일단 log찍어지는지 볼라고
logger = logging.getLogger("robotics-model")
app = FastAPI(title="Robotics Model Server", version="0.1")

class InputPayload(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def do_predict(payload: InputPayload):
    start = time.time()
    REQUESTS_TOTAL.labels(route="/predict").inc()
    if len(payload.features) != 4:
       FAIL_TOTAL.labels(route="/predict", reason="bad_input").inc()
       raise HTTPException(status_code=400, detail="features 길이는 4여야 합니다.")
    prob = predict(payload.features)
    drift.observe_sample(payload.features)
     CONFIDENCE_HIST.observe(prob)
     if prob <= float(os.getenv("LOWCONF_THRESHOLD", "0.6")):
         LOWCONF_TOTAL.inc()
     SUCCESS_TOTAL.labels(route="/predict").inc()
     DURATION.observe(time.time() - start)
     logger.info(f"[predict] 입력={payload.features} 결과={prob:.3f}")
     return {"probability": prob}

@app.get("/info")
def info():
    return {
       "model_version": os.getenv("MODEL_VERSION", "v1"),
       "commit": os.getenv("GIT_COMMIT", "?"),
       "environment": os.getenv("ENV", "local")
    }
