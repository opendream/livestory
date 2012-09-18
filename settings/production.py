from settings import *
#Alter or add production specific variables

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'livestory_live',
        'USER': 'livestory',
        'PASSWORD': 'livestory',
        'HOST': '',
        'PORT': '',
        }
}

# DJANGO-PRIVATE-FILES
FILE_PROTECTION_METHOD = 'nginx'

# DJANGO CELERY
CELERYD_LOG_FILE='/web/livestory/logs/celery.log'
