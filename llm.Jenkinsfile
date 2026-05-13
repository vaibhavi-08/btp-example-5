pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Checked out branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8 pytest
                '''
            }
        }

        stage('Quality') {
            steps {
                sh '''
                    . .venv/bin/activate
                    flake8 . \
                        --exclude=.venv,__pycache__,.git \
                        --max-line-length=100 \
                        --statistics \
                        --count
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest tests/ \
                        --tb=short \
                        -v
                '''
            }
        }

    }

    post {
        success {
            echo "Pipeline succeeded for branch: ${env.BRANCH_NAME}"
        }
        failure {
            echo "Pipeline FAILED. Check the logs above for details."
        }
        always {
            cleanWs()
        }
    }

}