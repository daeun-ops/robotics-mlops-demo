#!/usr/bin/env bash
set -euo pipefail

NS=robotics-platform

echo "[1/7] kubeconform (schema)"
make kube-validate

if kubectl get ns $NS >/dev/null 2>&1; then
  echo "[2/7] server dry-run"
  make k8s-dryrun || true

  echo "[3/7] service/routing 정합성"
  kubectl -n $NS get svc | grep robotics-model || true
  kubectl -n $NS get route || true
  kubectl -n $NS get virtualservice || true

  echo "[4/7] model server health/metric"
  POD=$(kubectl -n $NS get po -l app=robotics-model -o jsonpath='{.items[0].metadata.name}')
  kubectl -n $NS exec $POD -- curl -s localhost:8000/health | jq .
  kubectl -n $NS exec $POD -- sh -c "curl -s localhost:8000/metrics | head -n 20"

  echo "[5/7] drift exportor"
  kubectl -n $NS get svc drift-exporter && \
  kubectl -n $NS run tmp-curl --rm -i --image=curlimages/curl -q --restart=Never -- \
    curl -s drift-exporter.$NS.svc.cluster.local:9109/metrics | head -n 10 || true

  echo "[6/7] networkpolicy label  일치"
  kubectl -n $NS get deploy robotics-model -o jsonpath='{.spec.template.metadata.labels}' ; echo
  kubectl -n $NS get networkpolicy -o yaml | grep -A2 "podSelector:" | sed 's/^/  /'

  echo "[7/7] rollout/deploy status"
  kubectl -n $NS rollout status deploy/robotics-model || true
  which kubectl-argo-rollouts >/dev/null 2>&1 && kubectl argo rollouts get rollout robotics-model -n $NS || true
else
  echo "Namespace $NS not found. Skipping cluster checks."
fi

echo "✔ smoke done"


# chmod +x scripts/smoke.sh
# ./scripts/smoke.sh
