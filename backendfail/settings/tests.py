
SECRET_KEY="asd"
from basic import *
AUTHENTICATION_BACKENDS = [
    "settings.backends.TestcaseUserBackend",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

