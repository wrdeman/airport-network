jenkins_setup:
  cmd.run:
   - name: |
        wget -q -O - https://jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
        echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list
        apt-get update

jenkins:
  pkg:
    - installed

  service:
    - running
    - reload: True
    - watch:
      - pkg: jenkins

  user.present:
    - groups:
      - jenkins
      - vagrant

jenkins_cli:
  cmd.run:
   - name: |
        wget http://localhost:8080/jnlpJars/jenkins-cli.jar -P {{ pillar ['jenkins_cli'] }}
        java -jar {{ pillar ['jenkins_cli'] }}jenkins-cli.jar -s http://localhost:8080 install-plugin git
        java -jar {{ pillar ['jenkins_cli'] }}jenkins-cli.jar -s http://localhost:8080 create-job app < {{ pillar ['jenkins_conf'] }}/app.xml
        java -jar {{ pillar ['jenkins_cli'] }}jenkins-cli.jar -s http://localhost:8080 safe-restart
