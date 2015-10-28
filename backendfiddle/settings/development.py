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

