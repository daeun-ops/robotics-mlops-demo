"""
모델 서버의 /metrics를 읽어 confidence 히스토그램에서 간단 드리프트 수치 산출
실서비스는 로그/웨얼하우스 기반이 이상적. 데모에선 경량 HTTP 폴링.
"""
import os, time, requests
from prometheus_client import Gauge, start_http_server

TARGET = os.getenv("TARGET_METRICS", "http://robotics-model-svc.robotics-platform.svc.cluster.local/metrics")
PORT = int(os.getenv("PORT","9109"))
DRIFT = Gauge("confidence_drift", "확신도 분포 드리프트(간단 EMD 근사)")

def parse_buckets(txt):
    import re
    # inference_confidence_bucket{le="0.1"} 12 ...
    buckets = []
    for line in txt.splitlines():
      if line.startswith("inference_confidence_bucket"):
        m = re.search(r'le="([\d\.]+)".*}\s+(\d+)', line)
        if m:
          buckets.append((float(m.group(1)), int(m.group(2))))
    return buckets

def calc_emd(baseline, current):
    # 아주 단순한 누적차이 합
    import numpy as np
    b = np.array([v for _,v in baseline], dtype=float)
    c = np.array([v for _,v in current], dtype=float)
    b = b / max(b[-1],1.0); c = c / max(c[-1],1.0)
    return float(np.abs(np.cumsum(b)-np.cumsum(c)).sum())

BASE = None

if __name__ == "__main__":
    start_http_server(PORT)
    while True:
        try:
            r = requests.get(TARGET, timeout=3)
            cur = parse_buckets(r.text)
            if not cur: 
                time.sleep(5); continue
            global BASE
            if BASE is None:
                BASE = cur
            emd = calc_emd(BASE, cur)
            DRIFT.set(emd)
        except Exception:
            pass
        time.sleep(10)
