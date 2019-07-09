#!/usr/bin/env bash
echo '--> Setting environment to developer-portal STAGE'

export KUBECONFIG=${HOME}/.kube/k8s-developer-portal.config

# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT=stage
export K8S_NAMESPACE=dev-portal-${TARGET_ENVIRONMENT}

# Define an alias for the namespaced kubectl for convenience.
alias kc="kubectl -n ${K8S_NAMESPACE}"

export APP_SERVICE_CERT_ARN=arn:aws:acm:us-west-2:178589013767:certificate/ccc148ae-2a73-4551-84d4-f785f0d5e67e

export APP_REPLICAS=2
export APP_CPU_LIMIT=2
export APP_CPU_REQUEST=500m
export APP_MEMORY_LIMIT=4Gi
export APP_MEMORY_REQUEST=2Gi
export APP_GUNICORN_WORKERS=2
export APP_HOST=developer-portal-stage.mdn.mozit.cloud
