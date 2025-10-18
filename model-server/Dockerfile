FROM python:3.11-slim

# 비루트 사용자 생성 (보안)
RUN useradd -m appuser
WORKDIR /app
COPY app/ ./app/
RUN pip install --no-cache-dir -r app/requirements.txt

# OCI 메타데이터(레지스트리/보안 스캔에서 유용)
ARG GIT_COMMIT=unknown
LABEL org.opencontainers.image.source="?" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

USER appuser
EXPOSE 8000
# Healthcheck (런타임 자기진단)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8000/health || exit 1
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
