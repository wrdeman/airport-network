dev_requirements:
  pip.installed:
    - bin_env: {{ pillar['website_venv_bin'] }}
    - requirements: {{ pillar['dev_requirements_path'] }}
    - no_chown: True
