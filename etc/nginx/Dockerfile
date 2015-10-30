FROM nginx
RUN mkdir -p /etc/ssl
WORKDIR /etc/ssl
RUN openssl genrsa -out key.pem 2048
RUN openssl req -new -key key.pem -out csr.pem -subj "/C=DE/L=Nuremberg/O=backendfail"
RUN openssl req -x509 -days 365 -in csr.pem -key key.pem -out certificate.pem
WORKDIR /
RUN rm -rf /etc/nginx/conf.d/default
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN mkdir -p /mnt/media
RUN mkdir -p /mnt/static

