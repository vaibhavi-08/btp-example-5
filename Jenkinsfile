pipeline {
    agent any
    environment {
        REGISTRY_CREDS   = 'dockerhub-credentials'
        DEPLOY_SSH_CREDS = 'deploy-server-ssh'
        DOCKER_REGISTRY  = 'registry-1.docker.io'
    }
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
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }
        stage('Build') {
            steps {
                sh '''
                . venv/bin/activate || true
                python -m compileall .
                '''
            }
        }
        stage('Quality') {
            steps {
                sh '''
                . venv/bin/activate || true
                flake8 . || true
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                . venv/bin/activate || true
                pytest tests/ -v
                '''
            }
        }
    }
}