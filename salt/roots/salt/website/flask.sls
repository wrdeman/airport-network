{{ pillar['website_src_dir'] }}:
  file.directory:
    - user: vagrant
    - group: vagrant
    - mode: 755
    - makedirs: True
    - recurse:
      - user
      - group
      - mode


{{ pillar['website_venv_bin'] }}:
  file.directory:
    - user: vagrant
    - group: vagrant
    - mode: 755
    - makedirs: True
    - recurse:
      - user
      - group
      - mode

{{ pillar['bower_path'] }}:
  file:
    - managed
    - source: salt://website/bowerrc
    - template: jinja

git:
  pkg.installed

nodejs:
  pkg.installed

node_link:
  cmd.run:
    - name: ln -s /usr/bin/nodejs /usr/bin/node
npm:
  pkg.installed

bower:
  npm.installed:
    - require:
      - pkg: npm

app_requirements:
  pip.installed:
    - bin_env: {{ pillar['website_venv_bin'] }}
    - requirements: {{ pillar['website_requirements_path'] }}
    - no_chown: True
