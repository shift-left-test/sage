pipeline {
    agent {
	docker {
	    image "cart.lge.com/swte/yocto-dev:18.04"
	}
    }
    stages {
    	stage("Setup") {
	    steps {
		updateGitlabCommitStatus name: "jenkins", state: "running"
	    }
	}
	stage("Test") {
	    steps {
		sh "tox"
	    }
	}
    }  // stages
    post {
    	success {
            updateGitlabCommitStatus name: "jenkins", state: "success"
        }
        failure {
            updateGitlabCommitStatus name: "jenkins", state: "failed"
        }
	aborted {
	    updateGitlabCommitStatus name: "jenkins", state: "canceled"
	}
    }  // post
}  // pipeline
