from celery import Celery

from basic import *
DEBUG=True
def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG={
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
app = Celery('tasks', backend='rpc://', broker='amqp://')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: INSTALLED_APPS)


