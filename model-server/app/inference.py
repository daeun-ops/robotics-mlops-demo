"""
robotics model 예측 함수
실제 환경에서는 MLflow Model Registry에서 model을 load하도록 만금.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

# 간단한 dummy model임 테스트용
model = LogisticRegression()
model.coef_ = np.array([[0.5, -0.3, 0.1, 0.2]])

def predict(features: list[float]) -> float:
    """
    입력: 4차원 feature vector
    출력: 확률값 (0~1)
    """
    x = np.array(features).reshape(1, -1)
    y = model.predict_proba(x)[0, 1]
    return float(y)
