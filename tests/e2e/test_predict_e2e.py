"""
실제 서버 엔드포인트에 붙는 간단 E2E (CI에서 선택적으로 사용)
ENDPOINT=? 환경변수로 주입 (eg. http://localhost:8000)
"""
import os, requests, time

def test_predict_e2e():
    url = os.getenv("ENDPOINT", "http://localhost:8000")
    # 서버가 뜨는 시간 약간 대기
    for _ in range(10):
        try:
            if requests.get(url + "/health").status_code == 200:
                break
        except Exception:
            time.sleep(1)
    r = requests.post(url + "/predict", json={"features":[0.1,0.2,0.3,0.4]})
    assert r.status_code == 200 and "probability" in r.json()
