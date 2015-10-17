server{
  access_log /var/log/nginx/domain-access.log;

  location / {
    proxy_pass_header Server;
    proxy_set_header Host $host:$server_port;
    proxy_redirect off;
    proxy_set_header X-Forwarded-For  $remote_addr;
    proxy_set_header X-Scheme $scheme;
    proxy_connect_timeout 10;
    proxy_read_timeout 10;

    location /static/ {
      alias /home/vagrant/app/movies/static/;
      expires 1d;
    }


    proxy_pass http://127.0.0.1:8000/;
  }

}
