# Business Platform


## Overview


### Stacks
* Python 3.12
* Django 5.0
* ORM: SQLAlchemy with alembic data migration
* MySQL 9.0
* Nginx 1.27.1
* Redis 7.2.1


### There are 2 apps/services in this project: scada and bio


(Will add more for extending business logic)
* App scada: website 
* App bio: my profile


### Notes


* So far, either HTTPS over self-signed SSL on localhost for development only, or HTTP on a remote host.
* To generate self-signed SSL key pairs (it's fine for dev, but for prod, need to switch a CA one or Let's Encrypt for 90 days free with renewal):
  * ```openssl genpkey -algorithm RSA -out ssl_private.key```
  * ```openssl req -new -x509 -key ssl_private.key -out ssl_certificate.crt -days 36500```
* Currently, I'm using self-signed certificate which is not trusted by most browsers. `Let's Encrypt` can generate a free trusted certificate with a valid domain. 
* Now I don't have a domain name (need to purchase), so just keep HTTP request only. Later on, once a trusted certificate is ready, put them to `compose/nginx/ssl/`, and use `nginx_ssl.conf` instead in `compose/nginx/Dockerfile`.


* Any update in static folder of an app, do `python manage.py collectstatic --noinput` on local, so the update can be applied to `STATIC_ROOT` on local. execute start.sh again. Don't need to restart container.
* In docker-compose.yml, I set data persist `./webapp:/business_platform/webapp`, so the update in `STATIC_ROOT` on local can be synced to `STATIC_ROOT` in container.
* The same on any update in folder `business_platform/webapp`, just need to restart container, then execute `start.sh` which contains `python manage.py collectstatic --noinput` for taking effect to static `volume`.


* Switch environment needs to update:
  * `manage.py`, `wsgi.py`, `asgi.py`, `start.sh`, `sqlalchemy_setup.py` (change setting path either `dev.py` pr `prod.py`)


### Demo


* YouTube link: (HTTPS on localhost)
  * https://youtu.be/IhuqY_uwLeA

