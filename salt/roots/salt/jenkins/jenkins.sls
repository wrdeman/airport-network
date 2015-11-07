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
