pipeline {
    agent any

    environment {
        CONFIG_FILE = 'pipeline.config'
        DEPLOY_SSH_CREDS = 'deploy-server-ssh'
        VENV_PATH = 'venv'
        DEPLOY_DIR = '/home/vaibhavi/apps/btp-example-5'
        REPORTS_DIR = 'reports'
    }

    stages {
        stage('checkout') {
            steps {
                // Use Jenkins SCM checkout (configured in job settings)
                checkout scm
                script {
                    // Parse pipeline.config (KEY=VALUE format)
                    def configLines = readFile(CONFIG_FILE).readLines()
                    def config = [:]
                    configLines.each { line ->
                        if (line && !line.trim().startsWith('#') && line.contains('=')) {
                            def parts = line.split('=', 2)
                            config[parts[0].trim()] = parts[1].trim()
                        }
                    }
                    env.DEPLOY_HOST = config.DEPLOY_HOST
                    env.DEPLOY_USER = config.DEPLOY_USER
                    env.DEPLOY_BRANCH = config.DEPLOY_BRANCH
                    env.APP_NAME = config.APP_NAME ?: 'btp-app'
                    env.APP_COMMAND = config.APP_COMMAND ?: 'python main.py'
                    env.APP_PORT = config.APP_PORT ?: ''
                    
                    echo "✅ Config loaded: ${APP_NAME} → ${DEPLOY_HOST}:${APP_PORT ?: 'N/A'}"
                }
            }
        }

        stage('setup') {
            steps {
                script {
                    echo "📦 Setting up Python environment..."
                    sh '''
                        # Create isolated virtual environment
                        python3 -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        
                        # Upgrade pip and install dependencies
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            echo "   Installing from requirements.txt..."
                            pip install -r requirements.txt
                        else
                            echo "   ⚠️ No requirements.txt found"
                        fi
                        
                        # Install quality + test tools
                        pip install --quiet flake8 pytest pytest-cov pytest-junit
                        echo "✅ Environment ready: Python $(python --version)"
                    '''
                }
            }
        }

        stage('build') {
            steps {
                script {
                    // No Docker: "build" = prepare deployment artifact
                    echo "🔨 Preparing deployment package..."
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        
                        # Create deployment directory
                        mkdir -p deploy-package
                        
                        # Copy application code (exclude venv, git, cache, reports)
                        rsync -av --exclude='${VENV_PATH}' \
                              --exclude='.git' \
                              --exclude='__pycache__' \
                              --exclude='*.pyc' \
                              --exclude='.pytest_cache' \
                              --exclude='${REPORTS_DIR}' \
                              --exclude='deploy-package' \
                              ./ deploy-package/
                        
                        # Generate frozen requirements for target environment
                        pip freeze > deploy-package/deploy-requirements.txt
                        
                        # Create deployment script
                        cat > deploy-package/deploy.sh << 'EOF'
#!/bin/bash
set -e
APP_DIR="${1:-/home/vaibhavi/apps/btp-example-5}"
APP_NAME="${2:-btp-app}"
APP_COMMAND="${3:-python main.py}"

echo "📦 Deploying ${APP_NAME} to ${APP_DIR}..."

# Create app directory
mkdir -p "${APP_DIR}"

# Copy files (exclude deploy script itself)
find . -maxdepth 1 -not -name 'deploy.sh' -not -name '.' -exec cp -r {} "${APP_DIR}/" \\;

# Setup virtual environment on target
cd "${APP_DIR}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
. venv/bin/activate
pip install --upgrade pip -q
pip install -q -r deploy-requirements.txt

echo "✅ Deployment complete: ${APP_DIR}"
EOF
                        chmod +x deploy-package/deploy.sh
                        
                        echo "✅ Package ready: deploy-package/ ($(du -sh deploy-package | cut -f1))"
                    '''
                }
            }
        }

        stage('quality') {
            steps {
                script {
                    echo "🔍 Running flake8 quality checks..."
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        
                        # CRITICAL errors: FAIL the build immediately
                        echo "   [1/2] Checking critical errors (E9,F63,F7,F82)..."
                        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics \
                            --exclude=${VENV_PATH},.git,__pycache__,deploy-package,.pytest_cache,${REPORTS_DIR}
                        
                        # Style warnings: report only, don't fail build
                        echo "   [2/2] Checking style guidelines..."
                        flake8 . --count --exit-zero \
                            --max-complexity=10 \
                            --max-line-length=127 \
                            --statistics \
                            --exclude=${VENV_PATH},.git,__pycache__,deploy-package,.pytest_cache,${REPORTS_DIR}
                    '''
                    echo "✅ Quality checks passed"
                }
            }
        }

        stage('test') {
            steps {
                script {
                    echo "🧪 Running tests with pytest..."
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        
                        # Create reports directory
                        mkdir -p ${REPORTS_DIR}
                        
                        # Run pytest with coverage and JUnit XML output
                        # Supports both unittest and pytest-style tests
                        pytest tests/ -v \
                            --cov=. \
                            --cov-report=xml:${REPORTS_DIR}/coverage.xml \
                            --cov-report=html:${REPORTS_DIR}/coverage-html \
                            --junitxml=${REPORTS_DIR}/test-results.xml \
                            --cov-fail-under=0 \
                            || exit $?
                        
                        echo "✅ Tests complete"
                    '''
                }
                post {
                    always {
                        // Publish test results (JUnit format)
                        junit allowEmptyResults: true, testResults: "${REPORTS_DIR}/test-results.xml"
                        
                        // Publish HTML coverage report
                        publishHTML(target: [
                            allowMissing: true,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: "${REPORTS_DIR}/coverage-html",
                            reportFiles: 'index.html',
                            reportName: 'Test Coverage Report'
                        ])
                    }
                }
            }
        }

        stage('deploy') {
            when {
                branch "${env.DEPLOY_BRANCH}"
            }
            steps {
                script {
                    echo "🚀 Deploying ${APP_NAME} to ${DEPLOY_HOST}..."
                    
                    // Transfer package and deploy via SSH
                    sshagent(credentials: [DEPLOY_SSH_CREDS]) {
                        sh """
                            # Create remote app directory
                            ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 ${DEPLOY_USER}@${DEPLOY_HOST} \\
                                "mkdir -p ${DEPLOY_DIR}"
                            
                            # Copy deployment package to laptop
                            echo "   Transferring files..."
                            scp -o StrictHostKeyChecking=no -r deploy-package/* \\
                                ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_DIR}/
                            
                            # Execute deployment on laptop
                            echo "   Running deployment..."
                            ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 ${DEPLOY_USER}@${DEPLOY_HOST} \\
                                "cd ${DEPLOY_DIR} && \\
                                . venv/bin/activate && \\
                                pip install -q -r deploy-requirements.txt && \\
                                echo '   Stopping existing process...' && \\
                                pkill -f '${APP_NAME}' 2>/dev/null || true && \\
                                sleep 2 && \\
                                echo '   Starting ${APP_NAME}...' && \\
                                nohup ${APP_COMMAND} > ${APP_NAME}.log 2>&1 & \\
                                echo \$! > ${APP_NAME}.pid && \\
                                ${APP_PORT:+echo "   App listening on port ${APP_PORT}"} && \\
                                echo '✅ ${APP_NAME} started (PID: \$(cat ${APP_NAME}.pid))'"
                        """
                    }
                    echo "✅ Deployment complete: ${APP_NAME} running on ${DEPLOY_HOST}"
                }
            }
        }
    }

    post {
        always {
            // Archive test reports for historical viewing
            archiveArtifacts artifacts: "${REPORTS_DIR}/**/*", allowEmptyArchive: true, onlyIfSuccessful: false
            
            // Cleanup workspace
            cleanWs()
        }
        failure {
            echo '❌ Pipeline FAILED - Check console output for details'
            // Optional: Add email/Slack notification here
        }
        success {
            echo "🎉 SUCCESS: ${APP_NAME} deployed to ${DEPLOY_HOST}:${DEPLOY_DIR}"
            echo "   📊 View reports: Jenkins → ${JOB_NAME} #${BUILD_NUMBER} → 'Test Coverage Report'"
        }
        unstable {
            echo '⚠️ Pipeline UNSTABLE - Tests or quality checks had issues'
        }
    }
}