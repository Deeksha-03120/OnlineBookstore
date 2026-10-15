
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'online-bookstore'
        K8S_DEPLOYMENT = 'online-bookstore'
        K8S_SERVICE = 'online-bookstore-service'
        PYTHON_EXE = 'C:\\Users\\SENTHIL\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        DOCKER_SCOUT_EXE = 'C:\\Users\\SENTHIL\\.docker\\cli-plugins\\docker-scout.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Automated Tests') {
            steps {
                bat '"%PYTHON_EXE%" -m unittest discover -s tests -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'Dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat 'docker build --no-cache -t %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER% .'
                    bat 'docker tag %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER% %DH_USER%/%IMAGE_NAME%:latest'
                }
            }
        }

        stage('Security Gate') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'Dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat '"%DOCKER_SCOUT_EXE%" cves --exit-code --only-severity critical,high %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER%'
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'Dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat 'echo %DH_TOKEN%| docker login -u %DH_USER% --password-stdin'
                    bat 'docker push %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER%'
                    bat 'docker push %DH_USER%/%IMAGE_NAME%:latest'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    script {
                        try {
                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl set image deployment/%K8S_DEPLOYMENT% bookstore=%DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER%'
                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s'
                        } catch (err) {
                            echo 'Deployment failed. Attempting automatic rollback.'

                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout undo deployment/%K8S_DEPLOYMENT%'
                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s'

                            error('Deployment failed. Rollback attempted.')
                        }
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl get deployment %K8S_DEPLOYMENT%'
                    bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl get pods -l app=online-bookstore'
                    bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl get service %K8S_SERVICE%'
                    bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s'
                }
            }
        }
    }

    post {
        always {
            echo 'Online Bookstore pipeline finished.'
        }

        success {
            echo 'All tests and security checks passed. Deployment completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check Console Output to identify the failed stage.'
        }
    }
}
