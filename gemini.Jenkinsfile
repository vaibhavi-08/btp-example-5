pipeline {
agent any

options {
    skipDefaultCheckout()
}

environment {
    DEPLOY_SSH_CREDS = 'deploy-server-ssh'
}

stages {
    stage('Checkout') {
        steps {
            checkout scm
        }
    }

    stage('Setup') {
        steps {
            script {
                def props = readProperties file: 'pipeline.config'
                env.DEPLOY_HOST   = props.DEPLOY_HOST
                env.DEPLOY_USER   = props.DEPLOY_USER
                env.DEPLOY_BRANCH = props.DEPLOY_BRANCH
            }
            
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

    stage('Deploy') {
        when {
            branch "${env.DEPLOY_BRANCH}"
        }
        steps {
            sshagent(credentials: [env.DEPLOY_SSH_CREDS]) {
                sh """
                    # Create deployment directory on your laptop
                    ssh -o StrictHostKeyChecking=no ${env.DEPLOY_USER}@${env.DEPLOY_HOST} 'mkdir -p ~/python_deploy'
                    
                    # Copy the build artifact
                    scp -o StrictHostKeyChecking=no project-build.tar.gz ${env.DEPLOY_USER}@${env.DEPLOY_HOST}:~/python_deploy/
                    
                    # Extract and setup environment on the laptop
                    ssh -o StrictHostKeyChecking=no ${env.DEPLOY_USER}@${env.DEPLOY_HOST} '
                        cd ~/python_deploy
                        tar -xzf project-build.tar.gz
                        rm project-build.tar.gz
                        
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        
                        # The project is now ready to be executed on your laptop
                        echo "Deployment successful to ${env.DEPLOY_HOST}"
                    '
                """
            }
        }
    }
}

post {
    always {
        cleanWs()
    }
}
}