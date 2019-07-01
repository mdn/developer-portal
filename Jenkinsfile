def get_commit_tag() {
  return sh([returnStdout: true, script: "git rev-parse --short=7 HEAD"]).trim()
}

node {
  stage('Prep') {
    checkout scm
    tag = get_commit_tag()
  }

  stage ('Buld Image'){
    python_app = docker.build('mdnwebdocs/developer-portal-app', '-f ./dockerfiles/Dockerfile.app .')
    node_app = docker.build('mdnwebdocs/developer-portal-static', '-f ./dockerfiles/Dockerfile.static .')
  }

  stage('Push Image') {
    println("Pushing images")
    python_app.push("latest")
    python_app.push("${tag}")

    node_app.push("latest")
    node_app.push("${tag}")
  }

  stage('Cleanup') {
    cleanWs(
      cleanWhenFailure: false
    )
  }
}

