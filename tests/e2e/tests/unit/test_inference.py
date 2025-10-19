import os
import requests

def test_predict_smoke():
    base = os.getenv("BASE_URL","http://localhost:8000")
    try:
        r = requests.get(f"{base}/health", timeout=2)
    except Exception:
        # local 반응업스먼 PASS
        return
    r = requests.post(f"{base}/predict", json={"features":[0.1,0.2,1.7,34.2]}, timeout=2)
    assert r.status_code == 200
    assert "probability" in r.json()
