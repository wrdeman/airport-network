/etc/supervisor/conf.d/website.conf:
  file:
    - managed
    - create: True
    - source: salt://website/supervisord.conf
    - template: jinja
    - require_in:
      - supervisored_gunicorn
    - require:
      - pkg: supervisor

{{ pillar ['website_gunicorn_conf_path'] }}:
  file:
    - managed
    - source: salt://website/gunicorn.conf.py
    - user: vagrant
    - group: vagrant
    - require_in:
      - supervisored_gunicorn

supervisor:
  pkg:
    - installed

gunicorn:
  pip.installed:
    - bin_env: {{ pillar ['website_venv_bin'] }}
    - require:
      - pkg: python-pip

supervisored_gunicorn:
  supervisord:
    - running
    - name: website_gunicorn
    - update: True
    - restart: True
    - watch:
      - file: /etc/supervisor/conf.d/website.conf
      - file: /home/vagrant/gunicorn.conf.py
    - require:
      - pkg: supervisor
      - pip: gunicorn