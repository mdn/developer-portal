def get_commit_tag() {
  return sh([returnStdout: true, script: "git rev-parse --short=7 HEAD"]).trim()
}

node {
  stage('Prep') {
    checkout scm
    tag = get_commit_tag()
  }

  stage ('Buld Image'){
    image = 'mdnwebdocs/developer-portal'
    sh "docker build -t ${image}:latest -t ${image}:${tag} ."
  }

  stage('Push Image') {
    println("Pushing images")
    sh "docker push ${image}:latest"
    sh "docker push ${image}:${tag}"
  }

  stage('Cleanup') {
    cleanWs(
      cleanWhenFailure: false
    )
  }
}
