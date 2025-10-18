import math, threading, time
from collections import deque
from prometheus_client import Gauge
from app.metrics import DRIFT_KL

WINDOW = deque(maxlen=2000)  # 최근 입력 2k 샘플
BASELINE = [0.1]*10          # 테흐트용 균등분포(10 bins)

def observe_sample(features):
    # 4D 입력을 단순 합산/정규화하여 0~1로 맵핑 → 10 bins 히스토그램
    s = sum(features) / (len(features)*1.0)
    s = max(0.0, min(1.0, s))
    WINDOW.append(s)

def kl_div(p, q):
    eps=1e-9
    return sum(pi*math.log((pi+eps)/(qi+eps)) for pi,qi in zip(p,q) if pi>0)

def worker():
    while True:
        time.sleep(30)
        if len(WINDOW) < 100:  # 표본 적으면 건너뗘
            continue
        bins = [0]*10
        for v in list(WINDOW):
            bins[min(9, int(v*10))] += 1
        total = float(sum(bins)) or 1.0
        p = [b/total for b in bins]
        DRIFT_KL.set(kl_div(p, BASELINE))

def start():
    threading.Thread(target=worker, daemon=True).start()
