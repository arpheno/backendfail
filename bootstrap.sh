#!/bin/sh -e
sudo apt-get -y update
sudo apt-get -y install python-dev g++ vim  npm curl git supervisor
curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python
sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install -g bower vulcanize
sudo pip install pytest-django pytest-xdist coverage
sudo pip install -r /vagrant/requirements.txt
cd /vagrant/backendfail/
bower install --allow-root
python manage.py migrate
