# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT ?= stage
export K8S_NAMESPACE ?= dev-portal-${TARGET_ENVIRONMENT}
export AWS_RESOURCE_STACK=dev-portal-${TARGET_ENVIRONMENT}
export AWS_REGION ?= us-west-2
export K8S_CLUSTER_SHORT_NAME ?= eks-oregon

# Define an alias for the namespaced kubectl for convenience.
export KC=kubectl -n ${K8S_NAMESPACE}

# Configure default django settings to prod
export DJANGO_SETTINGS_MODULE ?= developerportal.settings.production

export APP_SERVICE_NAME ?= wagtail
export APP_SERVICE_IDLE_TIMEOUT ?= 120

export APP_NAME ?= wagtail
export APP_PORT ?= 8000
export APP_IMAGE ?= mdnwebdocs/developer-portal

export APP_IMAGE_PULL_POLICY ?= IfNotPresent
export APP_REPLICAS ?= 3
export MAX_APP_REPLICAS ?= 6
export APP_CPU_LIMIT ?= 2
export APP_CPU_REQUEST ?= 1
export APP_MEMORY_LIMIT ?= 4Gi
export APP_MEMORY_REQUEST ?= 2Gi
export APP_GUNICORN_WORKERS ?= 3
export APP_GUNICORN_TIMEOUT ?= 118
export APP_BASE_URL ?= https://${APP_HOST}
export APP_CDN_URL ?= https://${APP_CDN_HOST}
export APP_SUPPLEMENTARY_URL ?= https://${APP_SUPPLEMENTARY_HOST}
export APP_MOUNT_PATH ?= /app/media

export APP_EMAIL_HOST ?= email-smtp.us-west-2.amazonaws.com
export APP_EMAIL_PORT ?= 587
export APP_EMAIL_USE_TLS ?= True
export APP_SECURE_HSTS_SECONDS = 31536000

# Automatic content loading from other sources
export APP_AUTOMATICALLY_INGEST_CONTENT ?= True
export APP_NOTIFY_AFTER_INGESTING_CONTENT ?= False

# Task-completion survey config
export APP_TASK_COMPLETION_SURVEY_URL ?= undefined
export APP_TASK_COMPLETION_SURVEY_PERCENTAGE ?= 5.00  # default 5%

# Rate limiting
export APP_RATELIMIT_ENABLE ?= True

export CELERY_WORKER_NAME ?= celery-worker
export CELERY_WORKER_REPLICAS ?= 1
export CELERY_WORKER_CONCURRENCY ?= 2
export CELERY_WORKER_CPU_REQUEST ?= 100m
export CELERY_WORKER_MEMORY_REQUEST ?= 512Mi
export CELERY_WORKER_CPU_LIMIT ?= 2
export CELERY_WORKER_MEMORY_LIMIT ?= 1024Mi

export CELERY_SCHEDULER_NAME ?= celery-beat
export CELERY_SCHEDULER_REPLICAS ?= 1
export CELERY_SCHEDULER_CONCURRENCY ?= 1
export CELERY_SCHEDULER_CPU_REQUEST ?= 100m
export CELERY_SCHEDULER_MEMORY_REQUEST ?= 128Mi
export CELERY_SCHEDULER_CPU_LIMIT ?= 2
export CELERY_SCHEDULER_MEMORY_LIMIT ?=256Mi

# New relic config
export NEW_RELIC_CONFIG_FILE ?= /app/etc/newrelic.ini
export NEW_RELIC_LICENSE_KEY ?= foo
export NEW_RELIC_LICENSE_KEY_BASE64 ?= $(shell echo -n "${NEW_RELIC_LICENSE_KEY}" | base64)
export NEW_RELIC_MONITOR_MODE ?= 1
export NEW_RELIC_LABELS ?= Project:developer-portal;Namespace:${K8S_NAMESPACE};Environment:${TARGET_ENVIRONMENT}

# Google Analytics
export GOOGLE_ANALYTICS ?= 0

# Var to switch favicon colour
export ACTIVE_ENVIRONMENT ?= production

# Backup config
export RDS_BACKUP_NAME ?= "dev-portal-rds-backups"
export RDS_BACKUP_DBTYPE ?= 'PGSQL'
export RDS_BACKUP_IMAGE ?= mdnwebdocs/mdn-rds-backup
export RDS_BACKUP_IMAGE_TAG ?= 88e1721
export RDS_BACKUP_DIR ?= "/backup"
export RDS_BACKUP_BUCKET ?= "s3://developer-portal-backups-178589013767/backups"
export RDS_BACKUP_DEBUG_MODE ?= 'false'
export RDS_BACKUP_ROLE_ARN ?= "arn:aws:iam::178589013767:role/developer-portal-backups-role"

###############################
### core tasks

k8s-ns:
	kubectl create ns ${K8S_NAMESPACE} | true

k8s-delete-ns:
	kubectl delete --ignore-not-found ns ${K8S_NAMESPACE}

k8s-services:
	j2 app.svc.yaml.j2 | ${KC} apply -f -

test-k8s-services:
	j2 app.svc.yaml.j2 | kubeval --strict --ignore-missing-schemas

k8s-delete-services:
	${KC} delete --ignore-not-found svc ${APP_SERVICE_NAME}

k8s-deployments: k8s-wagtail-deployments k8s-celery-deployments k8s-celery-beat-deployments

test-k8s-deployments: test-k8s-wagtail-deployments test-k8s-celery-deployments test-k8s-celery-beat-deployments

k8s-delete-deployments: k8s-delete-wagtail-deployments k8s-delete-celery-deployments k8s-delete-celery-beat-deployments

k8s-wagtail-deployments:
	env NEW_RELIC_APP_NAME=dev-portal-web-${TARGET_ENVIRONMENT} \
	j2 app.deploy.yaml.j2 | ${KC} apply -f -

test-k8s-wagtail-deployments:
	env NEW_RELIC_APP_NAME=dev-portal-web-${TARGET_ENVIRONMENT} \
	j2 app.deploy.yaml.j2 | kubeval --strict --ignore-missing-schemas

k8s-celery-deployments:
	env NEW_RELIC_APP_NAME=dev-portal-celery-${TARGET_ENVIRONMENT} \
	env DJANGO_SETTINGS_MODULE=developerportal.settings.worker \
	j2 celery.yaml.j2 | ${KC} apply -f -

test-k8s-celery-deployments:
	env NEW_RELIC_APP_NAME=dev-portal-celery-${TARGET_ENVIRONMENT} \
	env DJANGO_SETTINGS_MODULE=developerportal.settings.worker \
	j2 celery.yaml.j2 | kubeval --strict --ignore-missing-schemas

k8s-celery-beat-deployments:
	env NEW_RELIC_APP_NAME="" \
	j2 celery-beat.yaml.j2 | ${KC} apply -f -

test-k8s-celery-beat-deployments:
	env NEW_RELIC_APP_NAME="" \
	j2 celery-beat.yaml.j2 | kubeval --strict --ignore-missing-schemas

k8s-hpa:
	j2 hpa.yaml.j2 | ${KC} apply -f -

test-k8s-hpa:
	j2 hpa.yaml.j2 | kubeval --strict --ignore-missing-schemas

k8s-delete-hpa:
	${KC} delete --ignode-not-found deploy ${APP_NAME}

k8s-delete-wagtail-deployments:
	${KC} delete --ignore-not-found deploy ${APP_NAME}

k8s-delete-celery-deployments:
	${KC} delete --ignore-not-found deploy ${CELERY_WORKER_NAME}

k8s-delete-celery-beat-deployments:
	${KC} delete --ignore-not-found deploy ${CELERY_SCHEDULER_NAME}

k8s-rollout-status:
	${KC} rollout status deploy ${APP_NAME}
	${KC} rollout status deploy ${CELERY_WORKER_NAME}

k8s-rollback:
	${KC} rollout undo deploy ${APP_NAME}

k8s-history:
	${KC} rollout history deploy ${APP_NAME}

k8s-db-migration-job: k8s-delete-db-migration-job
	env NEW_RELIC_APP_NAME="" \
	j2 db-migration-job.yaml.j2 | ${KC} apply -f -
	env JOB_NAME=db-migration ./wait_for_job.sh

k8s-delete-db-migration-job:
	${KC} delete --ignore-not-found job db-migration

k8s-rds-backup-cronjob:
	j2 db-backups-cron.yaml.j2 | ${KC} apply -f -

k8s-delete-rds-backup-cronjob:
	${KC} delete --ignore-not-found cronjob dev-portal-rds-backup

k8s-jenkins-create-rbac:
	kubectl apply -f jenkins-rbac.yaml

k8s-jenkins-delete-rbac:
	kubectl delete -f jenkins-rbac.yaml

k8s-search-index-update-job: k8s-delete-search-index-update-job
	env NEW_RELIC_APP_NAME=dev-portal-web-${TARGET_ENVIRONMENT} \
	j2 search-index-update-job.yaml.j2 | ${KC} apply -f -
	env JOB_NAME=search-index-update ./wait_for_job.sh

k8s-delete-search-index-update-job:
	${KC} delete --ignore-not-found job search-index-update


### end core tasks
###############################

# These tasks don't have file targets
.PHONY: k8s-ns k8s-delete-ns k8s-services k8s-delete-services \
		k8s-deployments k8s-delete-deployments k8s-rollout-status \
		k8s-wagtail-deployments k8s-celery-deployments \
		k8s-delete-wagtail-deployments k8s-delete-celery-deployments \
		k8s-rollback k8s-history k8s-db-migration-job \
		k8s-delete-db-migration-job \
    k8s-search-index-update-job \ k8s-delete-search-index-update-job
