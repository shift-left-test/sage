pipeline {
  agent {
    docker {
      image "cart.lge.com/swte/python-dev:latest"
    }
  }
  stages {
    stage('test') {
      steps {
        sh "tox"
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
