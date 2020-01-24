#!/usr/bin/env bash
echo '--> Setting environment to developer-portal STAGE on mdn-apps-a cluster'

export KUBECONFIG=${HOME}/.kube/mdn-apps-a.config

# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT=stage
export K8S_NAMESPACE=dev-portal-${TARGET_ENVIRONMENT}

# Define an alias for the namespaced kubectl for convenience.
alias kc="kubectl -n ${K8S_NAMESPACE}"

export APP_SERVICE_CERT_ARN=arn:aws:acm:us-west-2:178589013767:certificate/b58fa23c-5bde-4855-868b-8e59b90a4e89
export APP_BUCKET_ROLE_ARN=arn:aws:iam::178589013767:role/developer-portal-stage-us-west-2-role

export APP_REPLICAS=2
export MAX_APP_REPLICAS=4
export APP_CPU_LIMIT=2
export APP_CPU_REQUEST=500m
export APP_MEMORY_LIMIT=4Gi
export APP_MEMORY_REQUEST=2Gi
export APP_GUNICORN_WORKERS=2
export APP_HOST=developer-portal.stage.mdn.mozit.cloud
export APP_EXPORTED_SITE_HOST=developer-portal-cdn.stage.mdn.mozit.cloud
export APP_AWS_BUCKET_NAME=developer-portal-stage-178589013767
export APP_AWS_STORAGE_BUCKET_NAME=devportal-media-stage
export APP_AWS_BUCKET_REGION=us-west-2

export GOOGLE_ANALYTICS=UA-49796218-59

export ACTIVE_ENVIRONMENT=staging
export APP_AUTOMATICALLY_INGEST_CONTENT=True
export APP_NOTIFY_AFTER_INGESTING_CONTENT=False
