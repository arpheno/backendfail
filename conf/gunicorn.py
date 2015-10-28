import multiprocessing

bind = "0.0.0.0:8000"
timeout = 30
workers = multiprocessing.cpu_count() * 2 + 1
pythonpath = "/var/www/bf/backendfail"
# accesslog = "/vagrant/logs/gunicorn-access-log.txt"
# errorlog = "/vagrant/logs/gunicorn-error-log.txt"
