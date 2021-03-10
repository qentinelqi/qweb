#!groovy
pipeline {
    options {
      timeout(time: 1, unit: 'HOURS')
    }
    agent none
    stages {
        stage('Static analysis & Unit tests') {
            parallel {
                stage('Linux analysis & unit tests') {
                agent {label 'robot-worker'}
                    steps {
                        withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                            sh 'pip install tox'
                            sh 'pip install flake8'
                            sh 'pip install coverage'
                            sh 'tox -- pipdeptree --warn suppress'
                            sh 'xvfb-run --auto-servernum tox -- pylint QWeb'
                            sh 'xvfb-run --auto-servernum tox -- pylint test'
                            sh 'xvfb-run --auto-servernum tox -- pylint *.py'
                            sh 'xvfb-run --auto-servernum tox -- flake8 --verbose --max-line-length=100 QWeb'
                            sh 'xvfb-run --auto-servernum tox -- flake8 --verbose --max-line-length=100 test/unit'
                            sh 'xvfb-run --auto-servernum tox -e py36 -- pydocstyle QWeb/keywords'
                            sh 'xvfb-run tox -- pytest -v --junit-xml=unittests.xml --cov=QWeb'
                            junit 'unittests.xml'
                            archiveArtifacts 'unittests.xml'
                        }
                    }
                }
                stage('Windows analysis & unit tests') {
                    agent {label 'windows-at-aws'}
                    steps {
                        withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                            bat 'tox -- python -m pipdeptree'
                            bat 'tox -- python -m pylint QWeb --disable=C0328'
                            bat 'tox -- python -m pylint test --disable=C0328'
                            bat 'tox -- python -m pytest -v --junit-xml=win_unittests.xml --cov=QWeb'
                            //bat 'tox -- python -m pip install --upgrade robotframework-lint'
                            //bat 'tox -- python -m rflint --ignore FileTooLong test/acceptance'
                            junit 'win_unittests.xml'
                            archiveArtifacts 'win_unittests.xml'
                        }
                    }
                }
            }
        }
        stage('Acceptance & system tests'){
            parallel {
                stage('Linux') {
                    stages {
                        stage('Chrome Linux') {
                            environment {
                                BROWSER = "chrome"
                            }
                            agent {label 'robot-worker'}
                            steps {
                                withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                                    sh 'pip install tox'
                                    sh 'pip install coverage'
                                    sh 'export DISPLAY=:88'
                                    sh 'Xvfb $DISPLAY -screen 0 1920x1080x24 & sleep 1'
                                    sh 'matchbox-window-manager -use_titlebar no &'
                                    sh label: 'Chrome version', returnStdout: false, script: 'google-chrome --version'
                                    sh label: 'Chrome driver version', returnStdout: false, script: 'chromedriver --version'
                                    retry(2) {
                                        sh 'tox -e py36 -- coverage run --append -m robot --exitonfailure -e jailed -e WITH_DEBUGFILE -v BROWSER:$BROWSER -d output/$BROWSER/py36 --name QWeb -L TRACE --xunit xunit_report.xml test/acceptance'
                                        sh 'tox -e py36 -- coverage run --append -m robot --exitonfailure -e jailed -i WITH_DEBUGFILE -v BROWSER:$BROWSER -d output/$BROWSER/py36_debug --name QWeb -b debug.txt test/acceptance'
                                    }
                                    sh 'tox -e py36 -- coverage run --append -m robot.rebot --merge -d output/$BROWSER/py36 -o output.xml -l log.html -r report.html output/$BROWSER/py36/output.xml output/$BROWSER/py36_debug/output.xml'
                                    sh 'tox -e py36 -- coverage html --directory=output/$BROWSER/py36/coverage'
                                    sh 'tox -e py36 -- coverage xml -o coverage.xml'
                                    sh 'tox -- python -m robot -e jailed -v BROWSER:$BROWSER -d system_output/$BROWSER/steam -L trace --pythonpath . --pythonpath test/system/steam/libraries test/system/steam/tests/steam.robot'
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts 'output/**/*'
                                    junit 'output/**/py36/xunit_report.xml'
                                    step([$class: 'CoberturaPublisher', coberturaReportFile: 'coverage.xml'])
                                }
                            }
                        }
                        stage('Firefox Linux') {
                            when {expression { return env.GIT_BRANCH == 'master' } }                            
                            environment {
                                BROWSER = "firefox"
                            }
                            agent {label 'robot-worker'}
                            steps {
                                withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                                    sh 'pip install tox'
                                    sh 'pip install coverage'
                                    sh label: 'Firefox version', returnStdout: false, script: 'firefox --version'
                                    sh label: 'Gecko driver version', returnStdout: false, script: 'geckodriver --version'
                                    sh 'export DISPLAY=:88'
                                    sh 'Xvfb $DISPLAY -screen 0 1920x1080x24 & sleep 1'
                                    sh 'matchbox-window-manager -use_titlebar no &'
                                    retry(2) {
                                        sh 'tox -e py36 -- coverage run --append -m robot --exitonfailure -e jailed -e WITH_DEBUGFILE -e PROBLEM_IN_FIREFOX -v BROWSER:$BROWSER -d output/$BROWSER/py36 --name QWeb -L TRACE --xunit xunit_report.xml test/acceptance'
                                        sh 'tox -e py36 -- coverage run --append -m robot --exitonfailure -e jailed -i WITH_DEBUGFILE -e PROBLEM_IN_FIREFOX -v BROWSER:$BROWSER -d output/$BROWSER/py36_debug --name QWeb -b debug.txt test/acceptance'
                                    }
                                    sh 'tox -e py36 -- coverage run --append -m robot.rebot --merge -d output/$BROWSER/py36 -o output.xml -l log.html -r report.html output/$BROWSER/py36/output.xml output/$BROWSER/py36_debug/output.xml'
                                    sh 'tox -e py36 -- coverage html --directory=output/$BROWSER/py36/coverage'
                                    sh 'tox -e py36 -- coverage xml -o coverage.xml'
                                    sh  'tox -- python -m robot -e jailed -v BROWSER:$BROWSER -d system_output/$BROWSER/steam -L trace --pythonpath . --pythonpath test/system/steam/libraries test/system/steam/tests/steam.robot'
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts 'output/**/*'
                                    junit 'output/**/py36/xunit_report.xml'
                                    step([$class: 'CoberturaPublisher', coberturaReportFile: 'coverage.xml'])
                                }
                            }
                        }
                    }
                }
                stage('Windows') {
                    stages {
                        stage('Chrome Windows') {
                            environment {
                                BROWSER = "chrome"
                            }
                            agent {label 'windows-at-aws'}
                            steps {
                                withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                                    bat label: 'Chrome version', returnStdout: false, script: 'echo Chrome version: & reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
                                    bat label: 'Chrome driver version', returnStdout: false, script: 'chromedriver --version'
                                    retry(2) {
                                        // GPU needs to be disabled when running in headless mode in our AWS Windows (probably due to missing updates).
                                        // See https://bugs.chromium.org/p/chromium/issues/detail?id=737678
                                        bat 'tox -e py36 -- python -m robot --exitonfailure -e jailed -e PROBLEM_IN_WINDOWS -e WITH_DEBUGFILE -v browser:%BROWSER% -v browser_options:"--disable-gpu" -d win_output/%BROWSER%/py36 --name QWeb -L TRACE --xunit xunit_report.xml test/acceptance'
                                        bat 'tox -e py36 -- python -m robot --exitonfailure -e jailed -i WITH_DEBUGFILE -v browser:%BROWSER% -v browser_options:"--disable-gpu" -d win_output/%BROWSER%/py36_debug --name QWeb -b debug.txt test/acceptance'
                                    }
                                    bat 'tox -e py36 -- python -m robot.rebot --merge -d win_output/%BROWSER%/py36 -o output.xml -l log.html -r report.html win_output/%BROWSER%/py36/output.xml win_output/%BROWSER%/py36_debug/output.xml'
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts 'win_output/**/*'
                                    junit 'win_output/**/py36/xunit_report.xml'
                                }
                            }
                        }
                        stage('Firefox Windows') {
                            when {expression { return env.GIT_BRANCH == 'master' } }                            
                            environment {
                                BROWSER = "firefox"
                            }
                            agent {label 'windows-at-aws'}
                            steps {
                                withCredentials([usernameColonPassword(credentialsId: 'JFROG_API_KEY_UPLOAD', variable: 'JFROG_API_KEY')]) {
                                    bat label: 'Gecko driver version', returnStdout: false, script: 'geckodriver --version'
                                    retry(2) {
                                        bat 'tox -e py36 -- python -m robot --exitonfailure -e jailed -e PROBLEM_IN_WINDOWS -e WITH_DEBUGFILE -e PROBLEM_IN_FIREFOX -v BROWSER:%BROWSER% -d win_output/%BROWSER%/py36 --name QWeb -L TRACE --xunit xunit_report.xml test/acceptance'
                                        bat 'tox -e py36 -- python -m robot --exitonfailure -e jailed -e PROBLEM_IN_FIREFOX -i WITH_DEBUGFILE -v BROWSER:%BROWSER% -d win_output/%BROWSER%/py36_debug --name QWeb -b debug.txt test/acceptance'
                                    }
                                    bat 'tox -e py36 -- python -m robot.rebot --merge -d win_output/%BROWSER%/py36 -o output.xml -l log.html -r report.html win_output/%BROWSER%/py36/output.xml win_output/%BROWSER%/py36_debug/output.xml'
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts 'win_output/**/*'
                                    junit 'win_output/**/py36/xunit_report.xml'
                                }
                            }
                        }
                    }
                }
            }
        }
        

        
    }

   
} 
