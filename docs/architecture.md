# Architecture

OKD/Kubernetes 위에서 학습–등록–배포–관측까지 자동화된 MLOps 아키텍처.  
설명은 최소, 동작이 핵심.

---

## 1. High-level

```text
GitHub Actions ── build/test/sign ──► Image Registry
        │                                   │
        │                           (Argo Rollouts)
        ▼                                   ▼
Airflow ──► MLflow/MinIO ──► Registry(Stage→Prod) ──► model-server (FastAPI)
                               ▲                          │
                               └──────── Prometheus/Grafana/Alertmanager
