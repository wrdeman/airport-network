python2:
  pkg:
    - installed
    - names:
      - python-dev
      - python
      - libzmq-dev
      - libatlas-base-dev
      - gfortran

pip:
  pkg:
    - installed
    - name: python-pip
    - require:
      - pkg: python2

ipython_notebook:
  pip:
    - installed
    - names:
      - jupyter
      - pyzmq
    - require:
      - pkg: pip
