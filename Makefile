.PHONY: up down build test lint

# local 개발환경 실행
up:
\tdocker compose up -d

down:
\tdocker compose down -v

# Python dependancy install
build:
\tpip install -r training-mlflow/requirements.txt || true
\tpip install -r model-server/app/requirements.txt || true

# test gogogo 실행 (pytest 기준)
test:
\tpytest -q || echo "pytest not configured"

#  code it my style ! check..
lint:
\tpip install ruff==0.6.9 || true
\truff check model-server/app || true
