pipeline {
agent any

options {
    skipDefaultCheckout()
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
                pip install --upgrade pip
                pip install -r requirements.txt
            '''
        }
    }

    stage('Build') {
        steps {
            // Packaging the project files into a tarball for transfer
            sh 'tar -czf project-build.tar.gz --exclude=venv --exclude=.git .'
        }
    }

    stage('Quality') {
        steps {
            sh '''
                . venv/bin/activate
                pip install flake8
                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
            '''
        }
    }

    stage('Test') {
        steps {
            sh '''
                . venv/bin/activate
                pip install pytest
                pytest tests/
            '''
        }
    }

}

post {
    always {
        cleanWs()
    }
}
}