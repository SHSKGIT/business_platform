# business_platform


There are 2 apps in this project: scada and bio.


To generate self-signed SSL key pairs (it's fine for dev, but need to switch a CA one or Let's Encrypt for 90 days free with renewal):
openssl genpkey -algorithm RSA -out ssl_private.key
openssl req -new -x509 -key ssl_private.key -out ssl_certificate.crt -days 36500

Currently, I'm using self-signed certificate which is not trusted by browsers. `Let's Encrypt` can generate a free trusted certificate with a valid domain. 
Now I don't have a domain name, so just keep http request only. I will comment out SSL in nginx.conf


Any update in static folder of an app, do `python manage.py collectstatic --noinput` on local, so the update can be applied to `STATIC_ROOT` on local.
In docker-compose.yml, I set data persist `./webapp:/business_platform/webapp`, so the update in `STATIC_ROOT` on local can be synced to `STATIC_ROOT` in container.
The same on any update in folder `business_platform/webapp`, just need to restart container, then execute start.sh, the update will take effect in container.


Switch environment needs to update:
manage.py, wsgi.py, asgi.py, start.sh, sqlalchemy_setup.py

