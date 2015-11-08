from celery import Celery

from basic import *

INSTALLED_APPS
SECRET_KEY
ALLOWED_HOSTS = ['backend.fail', 'localhost', 'nikola.eestec.net']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME'  : 'postgres',
        'USER'  : 'postgres',
        'HOST'  : 'db',
        'PORT'  : '5432',
    }
}
CACHES = {
    'default': {
        'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'cache:11211',
    }
}


def show_toolbar(request):
    return request.user.is_superuser


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar
}

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_KEY_PREFIX = ""

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
os.environ['wsgi.url_scheme'] = 'https'
os.environ['HTTPS'] = "on"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
COMPRESS_ENABLED = True
COMPRESS_JS_FILTERS = ["compressor.filters.closure.ClosureCompilerFilter"]
COMPRESS_CLOSURE_COMPILER_BINARY = "/usr/bin/closure-compiler"
COMPRESS_CLOSURE_COMPILER_ARGUMENTS = "--language_in ECMASCRIPT5"
COMPRESS_MINT_DELAY = 100
INSTALLED_APPS = INSTALLED_APPS + (
    'django_statsd',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)
STATSD_PATCHES = [
    'django_statsd.patches.db',
    'django_statsd.patches.cache',
]
STATSD_CLIENT = 'django_statsd.clients.toolbar'
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'django_statsd.panel.StatsdPanel',
]
TOOLBAR_STATSD = {
    'graphite': 'http://nikola.eestec.net:8005/render/',
}

STATSD_MODEL_SIGNALS = True
STATSD_CELERY_SIGNALS = True
STATSD_HOST = "nikola.eestec.net"
DEBUG=True
app = Celery('tasks', backend='rpc://messagequeue', broker='amqp://messagequeue')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: INSTALLED_APPS)


