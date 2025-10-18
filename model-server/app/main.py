"""
Fast api 기반의 robotics model serving API
- /health: healthCheck~
- /predict: 예측수행
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.inference import predict

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
    return {"probability": prob}
