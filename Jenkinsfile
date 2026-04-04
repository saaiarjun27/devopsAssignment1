// --------------------------------------------------------
// Jenkinsfile – ACEest Fitness & Gym BUILD Pipeline
// --------------------------------------------------------
// Declarative pipeline that pulls the latest code from
// GitHub and performs a clean build + test cycle.
// --------------------------------------------------------

pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12'
        APP_NAME       = 'aceest-fitness'
    }

    stages {

        // Stage 1 – Checkout source from GitHub
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
            }
        }

        // Stage 2 – Install dependencies
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // Stage 3 – Lint / Syntax check
        stage('Lint') {
            steps {
                echo '🔍 Running flake8 lint checks...'
                sh '''
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        // Stage 4 – Run unit tests
        stage('Test') {
            steps {
                echo '🧪 Running Pytest suite...'
                sh '''
                    python3 -m pytest test_app.py -v --tb=short
                '''
            }
        }

        // Stage 5 – Build Docker image
        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build -t ${APP_NAME}:${BUILD_NUMBER} .
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${APP_NAME}:latest
                '''
            }
        }
    }

    post {
        success {
            echo '✅ BUILD SUCCESSFUL – All stages passed.'
        }
        failure {
            echo '❌ BUILD FAILED – Check the stage logs above.'
        }
        always {
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
    }
}
