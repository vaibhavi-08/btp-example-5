pipeline {
    agent any


    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {


                sh '''
                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip

                    # Install dependencies
                    if [ -f "requirements.txt" ]; then
                        pip install -r requirements.txt
                    fi

                    # Install quality and testing tools
                    pip install flake8 pytest
                '''
            }
        }

        stage('Build') {
            when {
                branch env.DEPLOY_BRANCH
            }

            steps {
                sh '''
                    echo "Simple Python project - no Docker build required"
                '''
            }
        }

        stage('Quality') {
            steps {
                sh '''
                    . venv/bin/activate

                    flake8 .
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate

                    pytest tests/
                '''
            }
        }
    }

    post {

        success {
            echo 'Pipeline executed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }
    }
}