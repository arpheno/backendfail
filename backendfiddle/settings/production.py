try:
    from secret import DATABASE_NAME, DATABASE_PASSWORD, DATABASE_USER, SECRET_KEY
except:
    DATABASE_NAME = "backendfiddle"
    DATABASE_PASSWORD =  "backendfiddle"
    DATABASE_USER =  "backendfiddle"
    SECRET_KEY = "Lasjod"
from basic import *

INSTALLED_APPS
SECRET_KEY
ALLOWED_HOSTS = ['.backendfiddle.xyz','.djfiddle.xyz', 'localhost']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
def show_toolbar(request):
    return request.user.is_superuser

DEBUG_TOOLBAR_CONFIG={
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar
}
DEBUG=True

CACHE_MIDDLEWARE_ALIAS="default"
CACHE_MIDDLEWARE_SECONDS=30
CACHE_MIDDLEWARE_KEY_PREFIX=""

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# os.environ['wsgi.url_scheme'] = 'https'
# os.environ['HTTPS'] = "on"
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
COMPRESS_ENABLED=True
COMPRESS_JS_FILTERS=["compressor.filters.closure.ClosureCompilerFilter"]
COMPRESS_CLOSURE_COMPILER_BINARY="/usr/bin/closure-compiler"
COMPRESS_CLOSURE_COMPILER_ARGUMENTS="--language_in ECMASCRIPT5"
COMPRESS_MINT_DELAY=100
