from settings import *

DEBUG = True

### django_debug_toolbar configurations

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

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
