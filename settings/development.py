from settings import *

DEBUG = True

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