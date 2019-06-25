
def get_commit_tag() {
  return sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
}

node {
  stage('Prep') {
    checkout scm
    tag = get_commit_tag()
  }

  stage ('Buld Image'){
    python_app = docker.build('mdnwebdocs/developer-portal-app:${tag}', '-f ./dockerfiles/Dockerfile.app .')
    node_app = docker.build('mdnwebdocs/developer-portal-static:${tag}', '-f ./dockerfiles/Dockerfile.static .')
  }

  stage('Push Image') {
    printlin("Pushing images")
    python_app.push()
    python_app.push("latest")

    node_app.push()
    node_app.push("latest")
  }

  stage('Cleanup') {
    cleanWs(
      cleanWhenFailure: false
    )
  }
}
