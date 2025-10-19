# robotics-mlops-demo/Makefile
.PHONY: up down build test lint kube-validate k8s-dryrun ros2-sim

# 로컬 스택
up:
\tdocker compose up -d

down:
\tdocker compose down -v

# 의존성 설치
build:
\tpip install -r training-mlflow/requirements.txt
\tpip install -r model-server/app/requirements.txt || true
\tpip install jsonschema==4.23.0 || true

# 테스트 (최소 스모크)
test:
\tpytest -q || echo "pytest skipped"

# 린트 (통일)
lint:
\tpip install ruff==0.6.9 || true
\truff check model-server/app || true

# kubeconform로 K8s 매니페스트 검증 (스키마 레벨)
kube-validate:
\tcurl -L https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz | tar xz
\t./kubeconform -summary -strict -ignore-missing-schemas \
\t  -kubernetes-version 1.28 -recursive model-server monitoring security isolation

# 클러스터 서버 드라이런 (선택; KUBECONFIG 필요)
k8s-dryrun:
\tkubectl apply -n robotics-platform -f model-server/service.yaml --server-dry-run=server
\tkubectl apply -n robotics-platform -f model-server/route.yaml --server-dry-run=server || true
\tkubectl apply -n robotics-platform -f model-server/deployment.yaml --server-dry-run=server
\tkubectl apply -n robotics-platform -f monitoring/prometheus --server-dry-run=server || true

# ROS2 데모 (퍼블리셔 + 브리지)
ros2-sim:
\tpython edge/ros2/telemetry_publisher.py & sleep 1 && python edge/ros2/telemetry_bridge.py
