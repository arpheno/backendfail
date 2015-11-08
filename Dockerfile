FROM arpheno/dependencies
RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/containers
RUN mkdir /etc/gunicorn
ADD backendfail /usr/src/app/
RUN rm -f /usr/src/app/settings/secret.py
ADD etc/gunicorn/config.py /etc/gunicorn/
WORKDIR /usr/src/app
CMD python manage.py migrate --settings=settings.production && python manage.py collectstatic --noinput && gunicorn wsgi --config=/etc/gunicorn/config.py

