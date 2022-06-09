pipeline {
   agent { label 'ml_server' }

   stages {
      stage('Workspace Setup') {
          steps {
           // TBD: deal with fact that Jenkins names the remote 'mltk', while CPM.cmake wants it to be 'origin'
           sh '''
                jenkins_remote_name=`git remote show`
                git remote rename $jenkins_remote_name origin
           ''' // newline required
          }
      }
      stage('Configure/Install MLTK') {
          steps {
              sh '''#!/usr/bin/bash
                export TMP=/data/tmp
                export TEMP=/data/tmp
                python3.8 --version
                python3.8 ./install_mltk.py
                source ${WORKSPACE}/.venv/bin/activate
                pip3 install tensorflow==2.4.*
                pip3 install tensorflow-probability==0.12.2
              '''
          }
      }
      stage('Check MLTK CLI') {
          steps {
              sh '''#!/usr/bin/bash
                export TMP=/data/tmp
                export TEMP=/data/tmp
                source ${WORKSPACE}/.venv/bin/activate
                mltk --version
                mltk --help
              '''
          }
      }
      stage('Running MLTK Unit tests') {
          steps {
              sh '''#!/usr/bin/bash
                export TMP=/data/tmp
                export TEMP=/data/tmp
                source ${WORKSPACE}/.venv/bin/activate
                mltk utest cli,api,cpp,studio
              '''
          }
      }
   }
   
   post {
       always {
           emailext body: "See ${BUILD_URL}", recipientProviders: [requestor()], subject: "Jenkins: ${JOB_NAME}: Build status is ${currentBuild.currentResult}"
       }
       success {
           sh '''
                git push origin HEAD:jenkins/stable
           '''
       }
       regression {
           emailext body: "See ${BUILD_URL}", recipientProviders: [culprits()], subject: 'Jenkins: ${JOB_NAME}: Build stability regressed after your change', to: 'dariedle'
       }
   }
}
