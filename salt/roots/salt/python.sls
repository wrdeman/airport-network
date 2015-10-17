python2:
  pkg:
    - installed
    - names:
      - python-dev
      - python
      - libzmq-dev

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
