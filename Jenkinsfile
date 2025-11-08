pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout the repository
                checkout scm
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
          # Build image and tag it with date and build number so we can push a reproducible tag
          TAG=$(date +%Y%m%d)-${BUILD_NUMBER}
          echo "Building Docker image: aceest-fitness-app:${TAG} (post-tests)"
          docker build -t aceest-fitness-app:${TAG} .
          # Keep a 'latest' tag locally as well
          docker tag aceest-fitness-app:${TAG} aceest-fitness-app:latest
        '''
            }
        }

        stage('Push app image') {
            steps {
                // Push built image to Docker Hub using credentials stored in Jenkins (credentialId: dockercreds)
                withCredentials([usernamePassword(credentialsId: 'dockercreds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
            set -e
            echo "Logging into Docker Hub as ${DOCKER_USER}"
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

            # Use the same date-BUILD_NUMBER tag used at build time
            TAG=$(date +%Y%m%d)-${BUILD_NUMBER}
            REMOTE_IMAGE=${DOCKER_USER}/aceest-fitness-app:${TAG}

            echo "Tagging image aceest-fitness-app:${TAG} -> ${REMOTE_IMAGE}"
            docker tag aceest-fitness-app:${TAG} ${REMOTE_IMAGE}

            echo "Pushing ${REMOTE_IMAGE} to Docker Hub"
            docker push ${REMOTE_IMAGE}

            # Optional: logout
            docker logout || true
          '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
          file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE'),
          usernamePassword(credentialsId: 'dockercreds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')
        ]) {
                                                sh '''
                                set -e
                                export KUBECONFIG=${KUBECONFIG_FILE}

                                TAG=$(date +%Y%m%d)-${BUILD_NUMBER}
                                REMOTE_IMAGE=${DOCKER_USER}/aceest-fitness-app:${TAG}

                                echo "Applying k8s manifests (if any)"
                                if [ -d k8s ]; then
                                    kubectl apply -f k8s/
                                else
                                    echo "No k8s/ directory found; cannot apply manifests."
                                fi

                                echo "Updating deployment image to ${REMOTE_IMAGE}"
                                # Try to set the image on the deployment; fail if it doesn't exist
                                kubectl set image deployment/aceest-fitness-app aceest-fitness-app=${REMOTE_IMAGE} --record

                                echo "Waiting for rollout to finish"
                                kubectl rollout status deployment/aceest-fitness-app --timeout=120s
                            '''
        }
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
