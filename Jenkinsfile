pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://Your_Sonar_Host_URL'
        SONAR_AUTH_TOKEN = credentials('sonarqube') //Credential of SonarQube as setp in jenkins
        MONGO_URI = 'http://Your_MongoDB_Host_URL'
        MONGO_DB = 'new_ai_code_suggestions' //The name of Database
        MONGO_COLLECTION = 'ML_analysis_results' // The name of MongoDb collection
        SUGGESTION_COLLECTION='AI_Suggestions' // The name of collection where AI suggestions are to be stored
        SONAR_SCANNER_PATH = '/opt/sonar-scanner/bin' // Mention the internal path os Sonar-Scanner in the EC2 instance
        GEMINI_API_KEY = credentials('gemini_key')// Credential of Gemini API as setup in jenkins
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/kanni5353/Malicious-URL-Classification.git'// Specify the branch and URL of github repo
            }
        }

        stage('Set Up Virtual Env & Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests and Generate Coverage') {
            steps {
                sh '''
                     . venv/bin/activate
                    if [ -d "tests" ]; then
                        coverage run -m unittest discover -s tests -p "test_*.py"
                        coverage xml -o coverage.xml
                    else
                        echo "⚠️ No tests/ directory found. Skipping unit tests and coverage."
                        echo "<?xml version='1.0'?><coverage></coverage>" > coverage.xml
                    fi
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'sonarqube', variable: 'SONAR_TOKEN')]) {
                        sh '''
                             . venv/bin/activate
                            export PATH=${SONAR_SCANNER_PATH}:$PATH
                            sonar-scanner -Dsonar.login=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Sync to MongoDB') {
            steps {
                script {
                    def projectKey = sh(script: "grep '^sonar.projectKey=' sonar-project.properties | cut -d'=' -f2", returnStdout: true).trim()
                    def projectName = sh(script: "grep '^sonar.projectName=' sonar-project.properties | cut -d'=' -f2", returnStdout: true).trim()

                    def safeWorkspace = sh(script: 'echo ${WORKSPACE} | tr " " "_"', returnStdout: true).trim()
                    sh "mkdir -p ${safeWorkspace}/temp_results"
                    def jsonFile = "${safeWorkspace}/temp_results/sonar_results.json"

                    echo "Using project key: ${projectKey}"

                    withCredentials([string(credentialsId: 'sonarqube', variable: 'SONAR_TOKEN')]) {
                        sh """
                            curl -u ${SONAR_TOKEN}: \
                            \"${SONAR_HOST_URL}/api/measures/component?component=${projectKey}&metricKeys=\
code_smells,bugs,vulnerabilities,coverage,line_coverage,branch_coverage,\
duplicated_lines_density,duplicated_blocks,duplicated_lines,duplicated_files,\
sqale_index,sqale_rating,sqale_debt_ratio,\
reliability_rating,security_rating,security_review_rating,\
security_hotspots,security_hotspots_reviewed,\
complexity,cognitive_complexity,\
comment_lines,comment_lines_density,\
ncloc,lines,functions,classes,statements,files,\
tests,test_errors,test_failures,skipped_tests,test_success_density,\
alert_status\" \
                            -o \"${jsonFile}\"

                            if [ ! -s \"${jsonFile}\" ]; then
                                echo \"ERROR: Empty response from SonarQube API\"
                                exit 1
                            fi
                        """
                    }

                    echo "SonarQube JSON contents:"
                    sh "cat ${jsonFile}"

                    echo "Syncing to MongoDB..."
                  // The mongo env activated here is hard coded in my space. will give the details on what to install and setup in instance in another file.
                    sh """
                        . /home/ubuntu/mongoenv/bin/activate 
                        export PROJECT_KEY=\"${projectKey}\"
                        export PROJECT_NAME=\"${projectName}\"
                        export MONGO_URI=\"${MONGO_URI}\"
                        export MONGO_DB=\"${MONGO_DB}\"
                        export MONGO_COLLECTION=\"${MONGO_COLLECTION}\"
                        export SONAR_JSON=\"${jsonFile}\"

                        python3 /home/ubuntu/sync_to_mongo.py
                    """
                }
            }
        }

        stage('Generate AI Suggestions') {
            steps {
                echo "🤖 Running AI Suggestion Generator..."
                sh '''
                    . /home/ubuntu/mongoenv/bin/activate
                    export SONAR_HOST_URL=${SONAR_HOST_URL}
                    export SONAR_AUTH_TOKEN=${SONAR_AUTH_TOKEN}
                    export SONAR_PROJECT_KEY=$(grep '^sonar.projectKey=' sonar-project.properties | cut -d'=' -f2)
                    export MONGO_URI=${MONGO_URI}
                    export MONGO_DB=${MONGO_DB}
                    export MONGO_COLLECTION=${SUGGESTION_COLLECTION}
                    export GEMINI_API_KEY=${GEMINI_API_KEY}
                    export SONAR_JSON="${WORKSPACE}/temp_results/sonar_results.json"

                    python3 /home/ubuntu/final_ai.py
                '''
            }
        }

        stage('Generate Email Body') {
            steps {
                script {
                    sh '''
                        . /home/ubuntu/mongoenv/bin/activate
                        pip install --quiet --disable-pip-version-check pandas
                        export SONAR_JSON="${WORKSPACE}/temp_results/sonar_results.json"
                        python3 /home/ubuntu/generate_email_body.py
                    '''
                }
            }
        }

        stage('Send Email') {// To use this stage we have to configure the Email plugin of Jenkins.
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    def emailOutputFile = "${WORKSPACE}/temp_results/email_body.html"
                    def buildUrl = "${env.BUILD_URL ?: "${JENKINS_URL}job/${JOB_NAME}/${BUILD_NUMBER}/"}console"

                    def sonarProps = readFile('sonar-project.properties')
                    def projectNameMatch = sonarProps.split('\n').find { it.startsWith('sonar.projectName=') }
                    def projectName = projectNameMatch ? projectNameMatch.split('=')[1].trim() : 'SonarQube Project'

                    def emailBody = readFile(emailOutputFile)

                    emailext(
                        subject: "✅ SonarQube Report - ${projectName} [Build #${BUILD_NUMBER}]",
                        mimeType: 'text/html',
                        body: emailBody + "<br><br><a href='${buildUrl}'>🔍 View Console Output</a>",
                        to: 'kanishka2k15@gmail.com',
                        attachmentsPattern: 'ai_suggestions_report.xlsx'
                    )
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            echo "✅ Pipeline completed successfully!"
        }

        failure {
            script {
                def buildUrl = "${env.BUILD_URL ?: "${JENKINS_URL}job/${JOB_NAME}/${BUILD_NUMBER}/"}console"
                emailext(
                    subject: "❌ Jenkins Build Failed [Build #${BUILD_NUMBER}]",
                    body: "Build failed. Please check Jenkins for details:<br><br><a href='${buildUrl}'>🔍 View Console Output</a>",
                    mimeType: 'text/html',
                    to: 'kanishka2k15@gmail.com'
                )
            }
        }
    }
}
