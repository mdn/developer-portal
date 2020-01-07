def get_commit_tag() {
  /*
   * Return the 7-digit commit-hash of HEAD.
   */
  return sh([returnStdout: true, script: "git rev-parse --short=7 HEAD"]).trim()
}

def notify_slack(Map args, credential_id='slack-hook-devportal-notifications') {
    def command = "${env.WORKSPACE}/scripts/slack-notify.sh"
    withCredentials([string(credentialsId: credential_id, variable: 'HOOK')]) {
        for (arg in args) {
            command += " --${arg.key} '${arg.value}'"
        }
        command += " --hook '${HOOK}'"
        sh command
    }
}

def deploy(config, environment, cluster) {
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
    try {

      notify_slack([
        status: "Pushing to ${environment} (cluster: ${cluster})",
        message: "developer-portal image ${tag}"
      ])

      sh """
        . config/${config}.sh
        export APP_IMAGE_TAG=${tag}
        make k8s-db-migration-job
        make k8s-deployments
        make k8s-rollout-status
      """
      notify_slack([
        stage: "Deployed to ${environment} (cluster: ${cluster})",
        status: 'success'
      ])

    } catch(err) {
      notify_slack([
        stage: "Failed to deploy to ${environment} (cluster: ${cluster})",
        status: 'failure'
      ])
      throw err
    }
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
      stage ('Build Image') {
        try {
          sh "docker build --tag ${image}:latest --tag ${image}:${tag} ."
        } catch(err) {
          notify_slack([
            stage: "Build of latest-tagged developer-portal image",
            status: 'failure'
          ])
          throw err
        }
      }
      stage ('Test') {
        // Set UID and GID
        env['UID'] = sh(returnStdout: true, script: 'id -u jenkins').trim()
        env['GID'] = sh(returnStdout: true, script: 'id -g jenkins').trim()
        try {
            sh "scripts/ci-setup --build"
            sh "scripts/ci-tests"

            notify_slack([
              stage: "Running test on tag ${tag}",
              status: 'success'
            ])

        } catch (err) {
            notify_slack([
              stage: "Test run failed on tag ${tag}",
              status: 'failure'
            ])
            throw err
        } finally {
            sh "docker-compose down --volumes --remove-orphans"
        }
      }
      stage('Push Images') {
        sh "docker push ${image}:latest"
        sh "docker push ${image}:${tag}"
      }
      break

    case 'dev-push':
      stage('Deploy') {
        deploy('dev', 'dev', 'mdn-apps-a')
      }
      break

    case 'stage-push':
      stage('Deploy') {
        deploy('stage', 'stage', 'mdn-apps-a')
      }
      break

    case 'prod-push':
      stage('Deploy') {
        deploy('prod', 'prod', 'mdn-apps-a')
      }
      break

    default:
      stage ('Build Image')  {
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
