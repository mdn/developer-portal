def get_commit_tag() {
  /*
   * Return the 7-digit commit-hash of HEAD.
   */
  return sh([returnStdout: true, script: "git rev-parse --short=7 HEAD"]).trim()
}

def deploy(config) {
  /*
   * Start a rolling update of the K8s deployments.
   */
  // Before we start the rolling update, ensure that we can pull an image
  // tagged with the commit-hash of HEAD. We don't want Kubernetes trying
  // to pull an image that doesn't exist.
  sh "docker pull ${image}:${tag}"
  // Configure the environment, perform any database migrations if necessary,
  // start the rolling update, and finally, monitor until complete.
  dir('k8s') {
    sh """
      . config/${config}.sh
      export APP_IMAGE_TAG=${tag}
      make k8s-db-migration-job
      make k8s-deployments
      make k8s-rollout-status
    """
  }
}

node {
  stage('Prep') {
    checkout scm
    tag = get_commit_tag()
    image = 'mdnwebdocs/developer-portal'
  }

  switch (env.BRANCH_NAME) {
    case 'master':
      stage ('Buld Image') {
        sh "docker build --tag ${image}:latest --tag ${image}:${tag} ."
      }
      stage ('Test') {
        withEnv(["COMPOSE_FILE=docker-compose.test.yml"]) {
          sh "docker-compose up --detach"
          try {
              sh "docker-compose exec -T app ./manage.py migrate"
              sh "docker-compose exec -T app ./manage.py test"
          } finally {
              sh "docker-compose down --volumes --remove-orphans"
          }
        }
      }
      stage('Push Images') {
        sh "docker push ${image}:latest"
        sh "docker push ${image}:${tag}"
      }
      break

    case 'stage-push':
      stage('Deploy') {
        deploy('stage')
      }
      break

    case 'prod-push':
      stage('Deploy') {
        deploy('prod')
      }
      break

    default:
      stage ('Buld Image')  {
        sh "docker build --tag ${image}:${tag} ."
      }
      stage('Push Image') {
        sh "docker push ${image}:${tag}"
      }
      break
  }

  stage('Cleanup') {
    cleanWs(
      cleanWhenFailure: false
    )
  }
}
