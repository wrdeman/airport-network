# virtualenv setup

website_venv: site
website_venv_dir: /home/vagrant/venv
website_venv_bin: /home/vagrant/venv/site

# source code
website_src_dir: /home/vagrant/app
website_app_path: /home/vagrant/app/app
website_requirements_path: /home/vagrant/app/requirements.txt

#bower
bower_dir: scripts/bower_components
bower_path: /home/vagrant/app/.bowerrc

# gunicorn paths
website_gunicorn_bin_path: /home/vagrant/venv/site/bin/gunicorn
website_gunicorn_conf_path: /home/vagrant/gunicorn.conf.py

#dev requirements
dev_requirements_path: /home/vagrant/app/dev_requirements.txt

# wdb path
wdb_path: /home/vagrant/venv/site/bin/


# jenkins cli
jenkins_cli: /home/vagrant/
jenkins_conf: /home/vagrant/app/jenkins