FROM nginx
RUN mkdir -p /etc/ssl
WORKDIR /etc/ssl
RUN openssl genrsa -out key.pem 2048
RUN openssl req -new -key key.pem -out csr.pem -subj "/C=DE/L=Nuremberg/O=backendfail"
RUN openssl req -x509 -days 365 -in csr.pem -key key.pem -out certificate.pem
WORKDIR /
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY production.conf /etc/nginx/conf.d/backendfail.conf
COPY pep8.conf /etc/nginx/conf.d/pep8.conf
COPY staging.conf /etc/nginx/conf.d/nikola.conf
COPY local.conf /etc/nginx/conf.d/local.conf
RUN mkdir -p /mnt/media
RUN mkdir -p /mnt/static

