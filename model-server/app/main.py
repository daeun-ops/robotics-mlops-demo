"""
Fast api 기반의 robotics model serving API
- /health: healthCheck~
- /predict: 예측수행
"""
from fastapi import FastAPI, HTTPException
import os, logging
from pydantic import BaseModel
from app.inference import predict

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
    if len(payload.features) != 4:
        raise HTTPException(status_code=400, detail="features 길이는 4여야 합니다.")
    prob = predict(payload.features)
    logger.info(f"[predict] 입력={payload.features} 결과={prob:.3f}")  # ← 운영 로깅
    return {"probability": prob}

@app.get("/info")
def info():
    return {
       "model_version": os.getenv("MODEL_VERSION", "v1"),
       "commit": os.getenv("GIT_COMMIT", "?"),
       "environment": os.getenv("ENV", "local")
    }
