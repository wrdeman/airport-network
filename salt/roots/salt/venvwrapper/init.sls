{% from "venvwrapper/map.jinja" import venvwrapper with context %}

python-pip:
  pkg.installed

virtualenvwrapper:
  pip.installed:
    - require:
      - pkg: python-pip

{{ salt['pillar.get']('website_venv_dir', '/home/vagrant/Venv') }}:
  file.directory:
    - user: vagrant
    - group: vagrant
    - mode: 755
    - makedirs: True
    - recurse:
      - user
      - group
      - mode

venvwrapper_env:
  environ.setenv:
    - name: WORKON_HOME
    - value : {{ salt['pillar.get']('website_venv_dir', '/home/vagrant/Venv') }}
    - update_minion: True

venv_source:
  cmd.run:
   - env:
     - WORKON_HOME: {{ salt['pillar.get']('website_venv_dir', '/home/vagrant/Venv') }}
   - name: |
        source /usr/local/bin/virtualenvwrapper.sh
        mkvirtualenv {{ salt['pillar.get']('website_venv', 'site') }}

venv_postactivate:
  file.append:
    - name: {{ salt['pillar.get']('website_venv_bin', '/home/vagrant/Venv') }}/bin/postactivate
    - text:
      - export DJANGO_SETTINGS_MODULE={{ salt['pillar.get']('website_settings', '') }}
      - export PYTHONPATH={{ salt['pillar.get']('website_src_dir', '') }}

{% for usr in ['vagrant'] %}
user_env:
  file.append:
    - name: /home/{{ usr }}/.bashrc
    - text:
      - export WORKON_HOME={{ salt['pillar.get']('website_venv_dir', '/home/vagrant/Venv') }}
      - source /usr/local/bin/virtualenvwrapper.sh
{% endfor %}
