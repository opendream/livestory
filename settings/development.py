from settings import *

DEBUG = True

### django_debug_toolbar configurations

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('debug_toolbar')
INSTALLED_APPS = tuple(INSTALLED_APPS)

INTERNAL_IPS = ('127.0.0.1')

DEBUG_TOOLBAR_CONFIG = {
     'INTERCEPT_REDIRECTS': False,
}
###------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'livestory',
        'USER': 'livestory',
        'PASSWORD': 'livestory',
        'HOST': '',
        'PORT': '',
    }
}