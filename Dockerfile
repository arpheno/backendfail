FROM arpheno/dependencies
RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/containers
ADD requirements.txt .
ADD pytest.ini .
RUN pip install -r requirements.txt
RUN pip install gunicorn coverage
RUN mkdir /etc/gunicorn
ADD backendfail /usr/src/app/
RUN rm -f /usr/src/app/settings/secret.py
ADD etc/gunicorn/config.py /etc/gunicorn/
WORKDIR /usr/src/app
CMD pypy manage.py migrate --settings=settings.production && pypy manage.py collectstatic --noinput && gunicorn wsgi --config=/etc/gunicorn/config.py

