# Django settings for livestory project.

import os
base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True


MEDIA_ROOT = os.path.join(base_path, 'media/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(base_path, 'sitestatic/')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(base_path, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

AUTH_PROFILE_MODULE = 'account.Account'
LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'urls'


SECRET_KEY = 'hu56#4ven7_!nfbx7mn-u^bgg^%(c!6(h3jdw632d4k8drmijt'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.TimezoneMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(base_path, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'context_processors.site_information',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'djkombu',
    'djcelery',
    'taggit',

    'location',
    'blog',
    'account',
    'common',
    'statistic',
    'notification',

    'south',
    'django_nose',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/livestory.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'livestory': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
        }
}


EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'oxfram.livestory@gmail.com'
EMAIL_HOST_PASSWORD = 'openpassword'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[LiveStory] '


import djcelery
djcelery.setup_loader()

# OXFAM LIVESTORY SETTINGS ################################################################################

# Uniqu for your project
SITE_LOGO = 'static/img/logo-livestories.png'
SITE_LOGO_EMAIL = 'static/img/logo-oxfam_email.png'

BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'guest'
BROKER_PASSWORD = 'guest'
BROKER_VHOST = '/'
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

# LIVE STORY
SITE_NAME = 'Oxfam Live Stories'
ORGANIZATION_NAME = 'Oxfam'
CONTACT_EMAIL = 'info@oxfam.org.uk'
IMAGE_URL = MEDIA_URL + 'images/'
IMAGE_ROOT = MEDIA_ROOT + 'images/'
TEMP_ROOT = MEDIA_ROOT + 'temp/'
AVATAR_SIZE = '94x94'
AVATAR_TOP_SIZE = '24x24'
BLOG_PREVIEW_SIZE = '470x1000'
CAN_SHARE_SN = False
NOTIFICATION_POPUP_NUM = 7
PRIVATE = True

# DJANGO-NOSE
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-erase',
    '--cover-package='
        'account,'
        'blog,'
        'location,'
        'notification,'
        'statistic',
]

