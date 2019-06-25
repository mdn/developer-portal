
def get_commit_tag() {
	return sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
}

node {
	println "${env}"

	stage('Prep') {
		checkout scm
		tag = get_commit_tag()
	}

	stage ('Buld Image'){
		app = docker.build('mdnwebdocs/developer-portal')
	}

	stage('Push Image') {
		docker.withRegistry('https://registry.hub.docker.com') {
			app.push("${tag}")
			app.push("latest")
		}
	}

	stage('Cleanup') {
		cleanWs(
			cleanWhenFailure: false
		)
	}
}
