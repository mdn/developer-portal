#!/usr/bin/env bash
echo '--> Setting environment to developer-portal dev on mdn-apps-a cluster'

export KUBECONFIG=${HOME}/.kube/mdn-apps-a.config

# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT=dev
export K8S_NAMESPACE=dev-portal-${TARGET_ENVIRONMENT}

# Define an alias for the namespaced kubectl for convenience.
alias kc="kubectl -n ${K8S_NAMESPACE}"

export APP_SERVICE_CERT_ARN=arn:aws:acm:us-west-2:178589013767:certificate/a37692cc-97e8-460d-ba15-bb897b8fff29
export APP_BUCKET_ROLE_ARN=arn:aws:iam::178589013767:role/developer-portal-dev-us-west-2-role

export APP_REPLICAS=2
export APP_CPU_LIMIT=2
export APP_CPU_REQUEST=256m
export APP_MEMORY_LIMIT=2Gi
export APP_MEMORY_REQUEST=1Gi
export APP_GUNICORN_WORKERS=2
export APP_HOST=developer-portal.dev.mdn.mozit.cloud
export APP_EXPORTED_SITE_HOST=developer-portal-published.dev.mdn.mozit.cloud
export APP_AWS_BUCKET_NAME=developer-portal-dev-178589013767
export APP_AWS_STORAGE_BUCKET_NAME=devportal-media-dev
export APP_AWS_BUCKET_REGION=us-west-2

export GOOGLE_ANALYTICS=UA-49796218-59

export ACTIVE_ENVIRONMENT=development
