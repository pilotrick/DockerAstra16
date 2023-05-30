Estan en la configuracion del nginx para el odoo 16 para el websocket y la sincronizacion en tiempo real

Ojo = Cambiar el paremtro $server basado en la ip del servidor 

client_max_body_size 2000m;
proxy_buffers 16 64k;
proxy_buffer_size 128k;
proxy_read_timeout  14720s;
proxy_connect_timeout 14720s;
proxy_send_timeout  14720s;
keepalive_timeout 60 ;
sendfile on;
default_type  application/octet-stream;

location /websocket {
    proxy_pass http://$server:8072;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }

gzip on;
gzip_disable msie6;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 7;
gzip_buffers 16 8k;
gzip_http_version 1.1;
gzip_min_length 1000;
gzip_proxied expired no-cache no-store private auth;
