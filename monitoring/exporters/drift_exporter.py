import os, time, requests, re, numpy as np
from prometheus_client import Gauge, start_http_server

TARGET = os.getenv("TARGET_METRICS", "http://robotics-model-svc.robotics-platform.svc.cluster.local/metrics")
PORT   = int(os.getenv("PORT","9109"))
DRIFT  = Gauge("confidence_drift", "확신도 분포 드리프트(EMD 근사)")

def parse(txt):
    buckets=[]
    for line in txt.splitlines():
        if line.startswith("inference_confidence_bucket"):
            m=re.search(r'le="([\d\.]+)".*}\s+(\d+)', line)
            if m: buckets.append((float(m.group(1)), int(m.group(2))))
    return buckets

def emd(base, cur):
    b=np.array([v for _,v in base], dtype=float); c=np.array([v for _,v in cur], dtype=float)
    b=b/max(b[-1],1.0); c=c/max(c[-1],1.0)
    return float(np.abs(np.cumsum(b)-np.cumsum(c)).sum())

BASE=None
if __name__=="__main__":
    start_http_server(PORT)
    while True:
        try:
            cur=parse(requests.get(TARGET, timeout=3).text)
            if not cur: time.sleep(5); continue
            global BASE
            if BASE is None: BASE=cur
            DRIFT.set(emd(BASE,cur))
        except Exception: pass
        time.sleep(10)
