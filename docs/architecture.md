# Architecture

OKD/Kubernetes 위에서 학습–등록–배포–관측까지 자동화된 MLOps 아키텍처.  
설명은 최소, 동작이 핵심.

---


```text
GitHub Actions ── build/test/sign ──► Image Registry
        │                                   │
        │                           (Argo Rollouts)
        ▼                                   ▼
Airflow ──► MLflow/MinIO ──► Registry(Stage→Prod) ──► model-server (FastAPI)
                               ▲                          │
                               └──────── Prometheus/Grafana/Alertmanager



Components
	•	Airflow: 데이터 전처리, 학습, 모델 등록 자동화.
	•	MLflow / MinIO: 실험 결과와 모델 아티팩트 관리.
	•	Model Server (FastAPI): 실시간 예측, 헬스체크, 메트릭 노출.
	•	Argo Rollouts + Istio: 카나리 배포, 트래픽 제어, 무중단 롤백.
	•	Prometheus / Grafana: 지표 수집 및 시각화, 알람 관리.
	•	Kyverno / NetworkPolicy: 컨테이너 보안 및 통신 제어.
	•	GitHub Actions: 빌드, 테스트, 서명, 배포 자동화.

⸻

Flow Summary
	1.	데이터 수집/학습 → Airflow DAG 실행.
	2.	모델 등록 → MLflow Tracking & Registry 기록.
	3.	이미지 빌드/배포 → GitHub Actions → Argo Rollouts.
	4.	서빙 요청 처리 → Istio VirtualService 라우팅.
	5.	모니터링/알람 → Prometheus Rule 기반 감시.

⸻

Key Design
	•	OKD 기반, PSA Restricted 정책 준수.
	•	Namespace / Quota / HPA / PDB / Outlier Detection 적용.
	•	CI/CD + Canary + Rollback 일체화.
	•	실험–배포–모니터링 파이프라인 완전 자동화



