# robotics-mlops-demo

[![CI](https://github.com/daeun-ops/robotics-mlops-demo/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/daeun-ops/robotics-mlops-demo/actions/workflows/ci-cd.yaml)
[![CodeQL](https://github.com/daeun-ops/robotics-mlops-demo/actions/workflows/codeql.yml/badge.svg)](https://github.com/daeun-ops/robotics-mlops-demo/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/badge/release-auto-blue.svg)](#)
[![SLSA](https://img.shields.io/badge/slsa-provenance-green.svg)](#)

AI 모델 학습부터 배포까지 자동화된 MLOps 파이프라인입니다. 
OKD 기반 쿠버네티스 환경을 기준으로 설계했고 
문서는 짧게.. 리소스를 통해 파악하면 이해가 더 잘됩니다

---

```text
┌───────────────────────────────────────────────────────────────────┐
│ GitHub Actions → Build/Test/Sign → Argo Rollouts (Canary)         │
│                            ↓                                      │
│                      Prometheus/Grafana                           │
│                ↑                          ↓                       │
│          MLflow/MinIO ← Airflow DAGs → Model Server(FastAPI)      │
└───────────────────────────────────────────────────────────────────┘

---


# Stack ( 아직 못쓴 것도 팄어여)
	•	Platform: Kubernetes / OKD 4.x
	•	Pipeline: Airflow, MLflow Tracking + Registry
	•	Serving: FastAPI, Argo Rollouts (Canary)
	•	Storage: MinIO (S3), PostgreSQL
	•	Monitoring: Prometheus, Alertmanager, Grafana, OpenTelemetry
	•	Security: Kyverno, NetworkPolicy, PSA Restricted, Image Sign Verify
	•	CI/CD: GitHub Actions, Cosign, SLSA Provenance
	•	Infra: Kustomize



---
# 디렉토리 구조 (아직 추가 못한 리소스파일들이 잇어요.)

robotics-mlops-demo/
├─ model-server/                   # 모델 서빙 (FastAPI)
│  ├─ app/                         # API / 로깅 / 트레이싱
│  ├─ deployment.yaml              # Deployment + Probe + Lifecycle
│  ├─ hpa.yaml                     # Horizontal Pod Autoscaler
│  ├─ service.yaml                 # Stable Service
│  ├─ service-canary.yaml          # Canary Service
│  ├─ istio-virtualservice.yaml    # Istio VirtualService
│  ├─ istio-destinationrule.yaml   # 회로차단 / 재시도 / Outlier
│  ├─ route.yaml                   # OKD Route (외부 진입)
│  ├─ pdb.yaml                     # PodDisruptionBudget (무중단)
│  ├─ rollouts/                    # Argo Rollouts / Analysis Template
│  └─ keda-scaledobject.yaml       # KEDA 기반 오토스케일
│
├─ training-mlflow/                # 모델 학습 및 MLflow 등록
│  ├─ register_and_promote.py      # 모델 등록/승격 스크립트
│  ├─ Dockerfile
│  └─ requirements.txt
│
├─ data-pipeline-airflow/          # 데이터 파이프라인
│  ├─ dags/
│  │  ├─ retrain_pipeline.py       # 재학습 DAG
│  │  └─ synthetic_check_dag.py    # API 헬스체크 DAG
│  └─ gx/check_dataset.py          # 데이터 품질 검증
│
├─ monitoring/                     # 모니터링 및 알람
│  ├─ prometheus/                  # PrometheusRule / SLO / Alerts
│  ├─ grafana/                     # 대시보드 템플릿
│  └─ otel/                        # OpenTelemetry Collector 설정
│
├─ security/                       # 보안 정책
│  ├─ kyverno-disallow-root.yaml   # root 실행 금지
│  ├─ kyverno-readonly-dropcaps.yaml
│  ├─ kyverno-verify-images.yaml   # 이미지 서명 검증
│  ├─ networkpolicy-default-deny.yaml
│  ├─ networkpolicy-egress-allow.yaml
│  └─ external-secret.yaml         # Vault / Secret Manager 연동
│
├─ isolation/                      # 리소스 격리
│  ├─ namespaces-and-quotas.yaml   # Namespace / Quota / LimitRange
│  ├─ node-affinity.yaml           # 전용 NodePool
│  └─ priority-classes.yaml        # PriorityClass
│
├─ logging/                        # 로그 정책
│  ├─ es-index-template.json       # Elasticsearch Index Template
│  └─ es-ilm-policy.json           # ILM 정책 (30일 보존)
│
├─ ops/                            # 운영 스크립트
│  ├─ backup/backup.sh             # MLflow / MinIO 백업
│  └─ restore.md                   # 복구 절차
│
├─ tests/                          # 테스트
│  ├─ e2e/                         # End-to-End
│  ├─ perf/                        # k6 부하 테스트
│  └─ unit/                        # 단위 테스트
│
├─ docs/                           # 최소한의 문서
│  ├─ architecture.md              # 아키텍처 개요
│  ├─ slo.md                       # SLO 정의
│  └─ runbooks/
│     ├─ alerts.md                 # 알람 런북
│     └─ incident-scenarios.md     # 장애 시나리오 대응
│
├─ .github/workflows/              # CI/CD 및 보안
│  ├─ ci-cd.yaml                   # 빌드 → 배포 → 카나리 검증
│  ├─ codeql.yml                   # 코드 보안 스캔
│  ├─ dependabot.yml               # 종속성 자동 업데이트
│  └─ slsa-provenance.yml          # 공급망 신뢰 증명
│
└─ README.md


---
## Features
	•	무중단 배포: Argo Rollouts + Istio OutlierDetection + PDB
	•	MLOps 파이프라인: Airflow → MLflow → Registry → Serving 자동화
	•	모니터링/알람: Prometheus SLO, CrashLoop, HPA 포화, 의존성 감시
	•	보안 정책: Kyverno / NetworkPolicy / PSA Restricted
	•	격리 전략: Namespace / Quota / Node Affinity / PriorityClass
	•	공급망 보안: SBOM + Cosign + SLSA Provenance
	•	로그 관리: JSON 마스킹 + Elastic ILM
	•	OKD 최적화: Route, SCC, mTLS 메시 통합


---
운영 기준으로 만든 프로젝트.
코드는 설명보다 많고, 리소스는 말이 빠르다.








