pipeline {
  agent {
    docker {
      image "cart.lge.com/swte/ubuntu-dev:latest"
    }
  }
  stages {
    stage('py2') {
      steps {
        sh "tox -e py2"
      }
      post {
        success {
          junit 'result.xml'
          cobertura coberturaReportFile: 'coverage.xml'
        }
      }
    }
    stage('py3') {
      steps {
        sh "tox -e py3"
      }
      post {
        success {
          junit 'result.xml'
          cobertura coberturaReportFile: 'coverage.xml'
        }
      }
    }
  }
}
