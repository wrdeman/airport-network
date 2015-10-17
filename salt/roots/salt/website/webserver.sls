nginx:
  pkg:
    - installed
    - names:
      - nginx

  service:
    - running
    - reload: True
    - watch:
      - pkg: nginx
      - file: /etc/nginx/sites-enabled/default

/etc/nginx/sites-enabled/default:
  file:
    - managed
    - source: salt://website/nginx.app
    - template: jinja
    - user: root
    - group: root
    - mode: 644
