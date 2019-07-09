# Define defaults for environment variables that personalize the commands.
export TARGET_ENVIRONMENT ?= stage
export K8S_NAMESPACE ?= dev-portal-${TARGET_ENVIRONMENT}
export AWS_RESOURCE_STACK=dev-portal-${TARGET_ENVIRONMENT}
export AWS_REGION ?= us-west-2
export K8S_CLUSTER_SHORT_NAME ?= eks-oregon

# Define an alias for the namespaced kubectl for convenience.
export KC=kubectl -n ${K8S_NAMESPACE}

export APP_SERVICE_NAME ?= wagtail
export APP_SERVICE_IDLE_TIMEOUT ?= 120

export APP_NAME ?= wagtail
export APP_PORT ?= 8000
export APP_IMAGE ?= mdnwebdocs/developer-portal

export APP_IMAGE_PULL_POLICY ?= IfNotPresent
export APP_REPLICAS ?= 3
export APP_CPU_LIMIT ?= 2
export APP_CPU_REQUEST ?= 1
export APP_MEMORY_LIMIT ?= 4Gi
export APP_MEMORY_REQUEST ?= 2Gi
export APP_GUNICORN_WORKERS ?= 3
export APP_GUNICORN_TIMEOUT ?= 118
export APP_BASE_URL ?= https://${APP_HOST}


###############################
### core tasks

k8s-ns:
	kubectl create ns ${K8S_NAMESPACE} | true

k8s-delete-ns:
	kubectl delete --ignore-not-found ns ${K8S_NAMESPACE}

k8s-services:
	j2 app.svc.yaml.j2 | ${KC} apply -f -

k8s-delete-services:
	${KC} delete --ignore-not-found svc ${APP_SERVICE_NAME}

k8s-deployments:
	j2 app.deploy.yaml.j2 | ${KC} apply -f -

k8s-delete-deployments:
	${KC} delete --ignore-not-found deploy ${APP_NAME}

k8s-rollout-status:
	${KC} rollout status deploy ${APP_NAME}

k8s-rollback:
	${KC} rollout undo deploy ${APP_NAME}

k8s-history:
	${KC} rollout history deploy ${APP_NAME}

k8s-db-migration-job: k8s-delete-db-migration-job
	j2 db-migration-job.yaml.j2 | ${KC} apply -f -
	env JOB_NAME=db-migration ./wait_for_job.sh

k8s-delete-db-migration-job:
	${KC} delete --ignore-not-found job db-migration

### end core tasks
###############################

# These tasks don't have file targets
.PHONY: k8s-ns k8s-delete-ns k8s-services k8s-delete-services \
		k8s-deployments k8s-delete-deployments k8s-rollout-status \
		k8s-rollback k8s-history k8s-db-migration-job \
		k8s-delete-db-migration-job
