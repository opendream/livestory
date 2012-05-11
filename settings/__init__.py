# Django settings for livestory project.

import os
BASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir)

ADMINS = (
    #('Opendream Support', 'support@opendream.co.th'),
    ('Opendream Support', 'panu@opendream.co.th'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True


MEDIA_ROOT = os.path.join(BASE_PATH, 'media/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_PATH, 'sitestatic/')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(BASE_PATH, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'urls'

AUTHENTICATION_BACKENDS = (
    'backends.EmailAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

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
    'django.middleware.transaction.TransactionMiddleware',
    'middleware.TimezoneMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, 'templates'),
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

# EASY THUMBNAILS ################################################################################

THUMBNAIL_DEBUG = True
THUMBNAIL_PRESERVE_EXTENSIONS = True

# LIVESTORY SETTINGS ################################################################################

SITE_NAME = 'Oxfam Live Stories'
SITE_DOMAIN = '127.0.0.1:8000'

ORGANIZATION_NAME = 'Oxfam'
CONTACT_EMAIL = 'info@oxfam.org.uk'

# BLOG

TEMP_BLOG_IMAGE_ROOT = os.path.join(MEDIA_ROOT, 'temp/blogging/')
TEMP_BLOG_IMAGE_URL = 'temp/blogging/'

BLOG_IMAGE_PREVIEW_WIDTH = 470
BLOG_IMAGE_PREVIEW_HEIGHT = 470
BLOG_IMAGE_PREVIEW_SIZE = '%dx%d' % (BLOG_IMAGE_PREVIEW_WIDTH, BLOG_IMAGE_PREVIEW_HEIGHT)

BLOG_IMAGE_ROOT = os.path.join(MEDIA_ROOT, 'images/blog/')
BLOG_IMAGE_URL = 'images/blog/'

PRIVATE = True

# Unique for your project
SITE_LOGO = 'static/img/logo-livestories.png'
SITE_LOGO_EMAIL = 'static/img/logo-oxfam_email.png'

# LIVE STORY

IMAGE_URL = MEDIA_URL + 'images/'
IMAGE_ROOT = MEDIA_ROOT + 'images/'
TEMP_ROOT = MEDIA_ROOT + 'temp/'

AVATAR_SIZE = '94x94'
AVATAR_TOP_SIZE = '24x24'
BLOG_PREVIEW_SIZE = '470x1000'

CAN_SHARE_SN = False
NOTIFICATION_POPUP_NUM = 7

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

# MAILGUN EMAIL SERVICE #########
CREATE_MAILBOX_AFTER_CREATE_USER = True

DEFAULT_FROM_EMAIL = 'postmaster@oxfamlivestories.org'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@oxfamlivestories.org'
EMAIL_HOST_PASSWORD = '9ayog9ixa9f8'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[LiveStory] '

USER_RESET_EMAIL_FROM = 'postmaster@oxfamlivestories.org'
INVITATION_EMAIL_FROM = 'postmaster@oxfamlivestories.org'

MAILGUN_API_DOMAIN = 'https://api.mailgun.net/v2/oxfamlivestories.org'
MAILGUN_API_KEY = 'key-9fju-vnl5spkmer1b2g2xtsxavhq2ai2'
MAILGUN_EMAIL_DOMAIN = 'oxfamlivestories.org'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_PATH, 'tmp/cache')
    }
}

