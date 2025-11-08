pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        // Checkout the repository
        checkout scm
      }
    }

    stage('Build app image') {
      steps {
        sh '''
          set -e
          echo "Building Docker image: aceest-fitness-app"
          docker build -t aceest-fitness-app .
        '''
      }
    }

    stage('Build test image') {
      steps {
        sh '''
          set -e
          echo "Building Docker test image: aceest-fitness-test (using testdockerfile)"
          docker build -f testdockerfile -t aceest-fitness-test .
        '''
      }
    }

    stage('Run tests in Docker') {
      steps {
        sh '''
          set -euo pipefail

          CONTAINER_NAME=testcontainer
          IMAGE_NAME=aceest-fitness-test

          docker container create --name ${CONTAINER_NAME} ${IMAGE_NAME} || true
          docker container start ${CONTAINER_NAME}
          EXIT_CODE=$(docker container wait ${CONTAINER_NAME})
          echo "Container exited with code ${EXIT_CODE}"

          echo "Attempting to copy /gym/report.xml from container to workspace"
          if docker cp ${CONTAINER_NAME}:/gym/report.xml ./report.xml; then
            echo "Copied report.xml"
          else
            echo "report.xml not found inside container"
          fi

          docker container rm ${CONTAINER_NAME} || true

          # If tests failed inside the container, exit with that code to abort the Jenkins stage.
          if [ "${EXIT_CODE}" -ne 0 ]; then
            echo "Tests failed (exit code ${EXIT_CODE}) — aborting stage"
            exit ${EXIT_CODE}
          fi
        '''
      }
    }
    
    stage('SonarQube Analysis') {
      steps {
        script {
          // Prefer Jenkins' SonarQube integration. SONAR_INSTALLATION can be set in job/env to override the default name 'SonarQube'.
          def sonarInstallation = 'sonarcloud'
          echo "Using SonarQube installation: ${sonarInstallation}"

          try {
            withSonarQubeEnv(sonarInstallation) {
              sh '''
                cat > sonar-project.properties <<'EOF'
                sonar.projectKey=aceest-fitness-py
                sonar.projectName=ACEest_Fitness_Py
                sonar.sources=src
                sonar.python.version=3.12
                sonar.sources.exclusions=**/tests/**,**/__pycache__/**,**/*.md
                sonar.junit.reportPaths=report.xml
                EOF
                sonar-scanner || true
                '''
            }
          } catch (err) {
            echo "withSonarQubeEnv failed or is not configured: ${err}"
            sh '''
            if command -v sonar-scanner >/dev/null 2>&1; then
            echo "Running sonar-scanner with SONAR_HOST_URL and SONAR_TOKEN if present"
            sonar-scanner -Dsonar.host.url=${SONAR_HOST_URL:-} -Dsonar.login=${SONAR_TOKEN:-} || true
            else
            echo "sonar-scanner not found; skipping SonarQube analysis"
            fi
            '''
          }
        }
      }
    }

    stage('Build app image') {
      steps {
        sh '''
          set -e
          echo "Building Docker image: aceest-fitness-app (post-tests)"
          docker build -t aceest-fitness-app .
        '''
      }
    }
  }

  post {
    always {
      // Archive the pytest report (if present) and record test results for Jenkins
      archiveArtifacts artifacts: 'report.xml', allowEmptyArchive: true
      junit testResults: 'report.xml', allowEmptyResults: true
    }
  }
}
