#!/usr/bin/env bash
# Deploy all k8s resources in dependency order
# Usage: ./k8s/apply.sh
set -e

echo "==> Applying namespace..."
kubectl apply -f k8s/namespace.yml

echo "==> Applying config and secrets..."
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secret.yml

echo "==> Deploying PostgreSQL..."
kubectl apply -f k8s/postgres/statefulset.yml
kubectl apply -f k8s/postgres/service.yml
kubectl rollout status statefulset/postgres -n irish-jobs

echo "==> Deploying Elasticsearch..."
kubectl apply -f k8s/elasticsearch/statefulset.yml
kubectl apply -f k8s/elasticsearch/service.yml
kubectl rollout status statefulset/elasticsearch -n irish-jobs

echo "==> Deploying backend..."
kubectl apply -f k8s/backend/deployment.yml
kubectl apply -f k8s/backend/service.yml
kubectl apply -f k8s/backend/hpa.yml
kubectl rollout status deployment/backend -n irish-jobs

echo "==> Applying ingress..."
kubectl apply -f k8s/ingress.yml

echo ""
echo "All resources deployed to namespace: irish-jobs"
kubectl get pods -n irish-jobs
