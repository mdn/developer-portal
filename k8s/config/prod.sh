#!/usr/bin/env bash
echo '--> Setting environment to developer-portal PROD on mdn-apps-a cluster'

export KUBECONFIG=${HOME}/.kube/mdn-apps-a.config

# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT=prod
export K8S_NAMESPACE=dev-portal-${TARGET_ENVIRONMENT}

# Define an alias for the namespaced kubectl for convenience.
alias kc="kubectl -n ${K8S_NAMESPACE}"

export APP_SERVICE_CERT_ARN=arn:aws:acm:us-west-2:178589013767:certificate/555815e9-a0c5-4bc5-9719-99b1389bf663
export APP_BUCKET_ROLE_ARN=arn:aws:iam::178589013767:role/developer-portal-prod-us-west-2-role

export APP_REPLICAS=4
export MAX_APP_REPLICAS=8
export APP_CPU_LIMIT=2
export APP_CPU_REQUEST=500m
export APP_MEMORY_LIMIT=4Gi
export APP_MEMORY_REQUEST=2Gi
export APP_GUNICORN_WORKERS=2
export APP_HOST=developer-portal.prod.mdn.mozit.cloud
export APP_CDN_HOST=developer.mozilla.com
export APP_AWS_BUCKET_NAME=developer-portal-prod-178589013767
export APP_AWS_STORAGE_BUCKET_NAME=devportal-media-prod
export APP_AWS_BUCKET_REGION=us-west-2

export CELERY_WORKER_CPU_REQUESTS=200m
export CELERY_WORKER_MEMORY_REQUEST=1Gi
export CELERY_WORKER_MEMORY_LIMIT=2Gi

export GOOGLE_ANALYTICS=UA-49796218-59

export ACTIVE_ENVIRONMENT=production
export APP_AUTOMATICALLY_INGEST_CONTENT=True
export APP_NOTIFY_AFTER_INGESTING_CONTENT=True

export APP_TASK_COMPLETION_SURVEY_URL=https://www.surveygizmo.com/s3/5499588/Mozilla-Dev-Portal-Task-Completion
export APP_TASK_COMPLETION_SURVEY_PERCENTAGE=5  # default in Makefile is 5, too
