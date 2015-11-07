#Airports
A little flask app to explore networkx, vega and some basic airport data.

My preference is Ubuntu, vagrant and lxc.

##Requirements
* [salt](https://docs.saltstack.com/en/latest/topics/tutorials/quickstart.html)
* [vagrant](https://docs.vagrantup.com/v2/)
* [lxc](https://github.com/fgrehm/vagrant-lxc)
* vagrant box fghrem/trusty64

```
# install vagrant
vagrant box add fghrem/trusty64
vagrant up

```

Check out [localhost:8000](http://localhost:8000)

NOTE: my salt state does start gunicorn properly. You need to start it manually, stop and then use supervisor!

Add this to .git/hooks/post-commit
```
#!/bin/sh                                                             |
echo "running jenkins"                                                |
curl -X POST --user jenkins:jenkins http://localhost:8080/job/app/build?delay=0sec
echo "saving jenkins config"                                          |
vagrant ssh -c "java -jar /home/vagrant/jenkins-cli.jar -s http://localhost:8080 get-job app > /home/vagrant/app/jenkins/app.xml"

```

Note: I have had to add a dummy JDK installation in jenkins because of a bug in the version on the [repository](https://issues.jenkins-ci.org/browse/JENKINS-31217)