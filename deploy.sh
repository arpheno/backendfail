#!/bin/sh
sudo
sudo pip install virtualenv
id -u somename &>/dev/null || sudo useradd gunicorn
cd /vagrant/
fab postgresql
fab graphite
. /vagrant/env/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2 python-memcached
sudo ln -sfn /vagrant/conf/supervisor.conf /etc/supervisor/conf.d/backendfiddle.conf -f
sudo ln -sfn /vagrant/conf/nginx.conf /etc/nginx/sites-enabled/backendfiddle.conf -f
cd /vagrant/backendfiddle
python manage.py migrate --settings=settings.production
python manage.py collectstatic --noinput  --settings=settings.production
