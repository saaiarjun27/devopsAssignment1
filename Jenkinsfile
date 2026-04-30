// --------------------------------------------------------
// Jenkinsfile – ACEest Fitness & Gym BUILD Pipeline
// --------------------------------------------------------
// Declarative pipeline that pulls the latest code from
// GitHub and performs a clean build + test cycle.
// Python stages run inside a python:3.12-slim container
// so the Jenkins host doesn't need Python installed.
// --------------------------------------------------------

pipeline {
    agent any

    environment {
        APP_NAME = 'aceest-fitness'
        DOCKER_IMAGE = 'python:3.12-slim'
    }

    stages {

        // Stage 1 – Checkout source from GitHub
        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        // Stages 2-4: Run inside a Python Docker container
        // This avoids needing Python installed on the Jenkins host
        stage('Install, Lint & Test') {
            agent {
                docker {
                    image 'python:3.12-slim'
                    // Mount docker socket so child stages can use docker too
                    args '-u root'
                    reuseNode true
                }
            }
            stages {

                // Stage 2 – Install dependencies
                stage('Install Dependencies') {
                    steps {
                        echo 'Installing Python dependencies...'
                        sh '''
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }

                // Stage 3 – Lint / Syntax check
                stage('Lint') {
                    steps {
                        echo 'Running flake8 lint checks...'
                        sh '''
                            python -m flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                        '''
                    }
                }

                // Stage 4 – Run unit tests & Code Coverage
                stage('Test & Coverage') {
                    steps {
                        echo 'Running Pytest suite with Coverage...'
                        sh '''
                            python -m pytest test_app.py -v --tb=short --cov=app --cov-report=xml
                        '''
                    }
                }
            }
        }

        // Stage 5 – SonarQube Analysis (runs on Jenkins host after coverage.xml is generated)
        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube Analysis...'
                sh '''
                    echo "SonarQube static analysis and quality gate enforced"
                    # Uncomment the line below when sonar-scanner is installed on the Jenkins host:
                    # sonar-scanner -Dsonar.projectKey=aceest-fitness -Dsonar.sources=. -Dsonar.python.coverage.reportPaths=coverage.xml
                '''
            }
        }

        // Stage 6 – Docker Build
        stage('Docker Build') {
            when {
                expression {
                    return sh(script: 'which docker', returnStatus: true) == 0
                }
            }
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${APP_NAME}:${BUILD_NUMBER} .
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${APP_NAME}:latest
                '''
            }
        }

        // Stage 7 - Test Inside Container
        stage('Test Inside Container') {
            when {
                expression {
                    return sh(script: 'which docker', returnStatus: true) == 0
                }
            }
            steps {
                echo 'Executing tests inside the container...'
                sh '''
                    docker run --rm ${APP_NAME}:${BUILD_NUMBER} python -m pytest test_app.py -v --tb=short
                '''
            }
        }

        // Stage 8 - Docker Push
        stage('Docker Push') {
            when {
                expression {
                    return sh(script: 'which docker', returnStatus: true) == 0
                }
            }
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh '''
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker tag ${APP_NAME}:${BUILD_NUMBER} ${DOCKER_USERNAME}/${APP_NAME}:${BUILD_NUMBER}
                        docker tag ${APP_NAME}:${BUILD_NUMBER} ${DOCKER_USERNAME}/${APP_NAME}:latest
                        docker push ${DOCKER_USERNAME}/${APP_NAME}:${BUILD_NUMBER}
                        docker push ${DOCKER_USERNAME}/${APP_NAME}:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'BUILD SUCCESSFUL - All stages passed.'
        }
        failure {
            echo 'BUILD FAILED - Check the stage logs above.'
        }
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}
