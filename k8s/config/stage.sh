#!/usr/bin/env bash
echo '--> Setting environment to developer-portal STAGE'

export KUBECONFIG=${HOME}/.kube/k8s-developer-portal.config

# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT=stage
export K8S_NAMESPACE=dev-portal-${TARGET_ENVIRONMENT}

# Define an alias for the namespaced kubectl for convenience.
alias kc="kubectl -n ${K8S_NAMESPACE}"

export APP_SERVICE_CERT_ARN=arn:aws:acm:us-west-2:178589013767:certificate/ccc148ae-2a73-4551-84d4-f785f0d5e67e
export APP_BUCKET_ROLE_ARN=arn:aws:iam::178589013767:role/developer-portal-stage-us-west-2-role

export APP_REPLICAS=2
export APP_CPU_LIMIT=2
export APP_CPU_REQUEST=500m
export APP_MEMORY_LIMIT=4Gi
export APP_MEMORY_REQUEST=2Gi
export APP_GUNICORN_WORKERS=2
export APP_HOST=developer-portal-dev.mdn.mozit.cloud
export APP_EXPORTED_SITE_HOST=developer-portal-published.dev.mdn.mozit.cloud
export APP_AWS_BUCKET_NAME=developer-portal-stage-178589013767
export APP_AWS_STORAGE_BUCKET_NAME=developer-portal-stage-media-178589013767
export APP_AWS_BUCKET_REGION=us-west-2
export APP_MOUNT_PATH=/app/media

export APP_PVC_NAME=developer-portal-stage
export APP_PVC_SIZE=100Gi
export APP_PV_NAME=developer-portal-stage
export APP_PV_STORAGE_CLASS_NAME=efs

export APP_PV_SIZE=100Gi
export APP_PV_RECLAIM_POLICY=Retain
export APP_PV_MOUNT_PATH=/
export APP_PV_ARN=fs-0baec5a0.efs.us-west-2.amazonaws.com

export GOOGLE_ANALYTICS=UA-49796218-59
