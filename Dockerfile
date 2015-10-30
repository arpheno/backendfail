FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y net-tools
RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/containers
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN mkdir /etc/gunicorn
RUN rm -f /usr/src/app/settings/secret.py
ADD backendfail /usr/src/app/
ADD etc/gunicorn/config.py /etc/gunicorn/
WORKDIR /usr/src/app
ENTRYPOINT python manage.py migrate --settings=settings.production && python manage.py collectstatic --noinput && gunicorn wsgi --config=/etc/gunicorn/config.py

