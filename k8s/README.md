# The Developer-Portal in Kubernetes

Most of these commands require special configuration and permissions available only to a limited number of Mozilla staff on the MDN team.

## Local Requirements:

- Install `kubectl` (the Kubernetes command-line tool) -- https://kubernetes.io/docs/tasks/tools/install-kubectl/

* Install `j2cli` (Jinja2 command-line tool)

```sh
pip install j2cli
```

- Install `jq` (lightweight/flexible command-line JSON processor)

```sh
brew update
brew install jq
```

- Move/copy your K8s configuration file for the cluster to `~/.kube/k8s-developer-portal.config`

## Deploying the Developer-Portal CMS

#### Setup

- Move to the `k8s` directory of the developer-portal repo

  ```sh
  cd k8s
  ```

- Configure your environment depending upon whether you're deploying to stage or production.

  - Stage

  ```sh
  source config/stage.sh
  ```

  - Production

  ```sh
  source config/prod.sh
  ```

#### Deploying

- Specify the developer-portal image tag you want to deploy. It must be available from DockerHub (see https://cloud.docker.com/u/mdnwebdocs/repository/docker/mdnwebdocs/developer-portal/tags for a list of available tags). New developer-portal images are built and registered on DockerHub after every commit to the `master` branch of https://github.com/mdn/developer-portal.

```sh
export APP_IMAGE_TAG=<tag-from-dockerhub>
```

- Run the database migrations

```sh
make k8s-db-migration-job
```

- Rollout the update

```sh
make k8s-deployments
```

- Update the search index

```sh
make k8s-search-index-update-job
```

- Monitor the status of the rollout until it completes

```sh
make k8s-rollout-status
```

- In an emergency, if the rollout is causing failures, you can roll-back to the previous state.

```sh
make k8s-rollback
```

#### Prerequisites

This section lists the one-time steps required before performing the deployment steps described above.

##### Provision AWS Resources and K8s Secrets

- Create an AWS RDS PostgreSQL instance
- Create a K8s secrets resource that provides the `DJANGO_SECRET_KEY`, `POSTGRES_HOST`, and `POSTGRES_PASSWORD` values
- Create an AWS SSL certificate (for the ELB) and use its ARN as the value for `APP_SERVICE_CERT_ARN`

##### Make the K8s namespace and services

This step requires special privileges for creating and configuring the ELB that will be created as part of the `make k8s-services` command.

```sh
make k8s-ns
make k8s-services
```
