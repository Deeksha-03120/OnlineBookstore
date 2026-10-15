
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'online-bookstore'
        K8S_DEPLOYMENT = 'online-bookstore'
        K8S_SERVICE = 'online-bookstore-service'
        PYTHON_EXE = 'C:\\Users\\SENTHIL\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
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
                    bat 'docker build -t %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER% .'
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
                    bat 'docker scout cves --only-severity critical,high %DH_USER%/%IMAGE_NAME%:%BUILD_NUMBER%'
                }
            }
        }

        stage('Push Docker Image') {
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
                    usernamePassword(
                        credentialsId: 'Dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    ),
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
                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout undo deployment/%K8S_DEPLOYMENT%'
                            bat 'set KUBECONFIG=%KUBECONFIG_FILE% && kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s'
                            error('Deployment failed. Rollback attempted.')
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Online Bookstore pipeline finished.'
        }
    }
}
