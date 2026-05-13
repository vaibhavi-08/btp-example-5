pipeline {
    agent any

    environment {
        
        VENV_PATH = 'venv'
    }

    stages {
        stage('checkout') {
            steps {
                // Use Jenkins SCM checkout (configured in job settings)
                checkout scm
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

    }
}