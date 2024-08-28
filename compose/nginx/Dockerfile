FROM nginx:latest

# need to remove default.conf, it routes to nginx webpage by default
RUN rm /etc/nginx/conf.d/default.conf \
&& mkdir -p /usr/share/nginx/html/static \
&& mkdir -p /usr/share/nginx/html/media \
&& mkdir -p /usr/share/nginx/ssl

# nginx default user www-data
RUN chown -R www-data:www-data /usr/share/nginx/html/media \
&& chmod -R 775 /usr/share/nginx/html/media

#ADD ./nginx.conf /etc/nginx/conf.d/
ADD ./nginx_ssl.conf /etc/nginx/conf.d/

RUN sed -i '/user/{s/nginx/root/}' /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]