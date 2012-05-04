from settings import *

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

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