# Django settings for example project.
import os
import sys

PROJECT_DIR = os.path.abspath('%s/../' % os.path.dirname(__file__))
APP_DIR = os.path.abspath('%s/../../' % os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)

DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}
USE_TZ = True
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(MEDIA_ROOT, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+3^08&lnsm^nl1iozv=a-9!e4x$*o%g6pkx=y$)oc8#r$ndn7t'

# List of callables that know how to import templates from various sources.
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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, "templates"),
)

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
)

THIRDPARTY_APPS = (
    'bootstrapform',
    'south',
)

PROJECT_APPS = (
    'events',
    'gunicorn',
    'quotes',
    'admin_views',
    'rest_framework',
    'audience',
)

BASE_APPS = DJANGO_APPS + THIRDPARTY_APPS
INSTALLED_APPS = DJANGO_APPS + THIRDPARTY_APPS + PROJECT_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'utils.context_processors.site',
)

FIRST_DAY_OF_WEEK = 1  # Monday

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/signin/'

AUDIENCE_SETTINGS = {
    'AUDIENCE_TYPES': {
        5: {'name': 'Kid',
            'plural_name': 'Kids',
            'code': 'KD',
            'description': 'Grades K-5',
            'default_text_difficulty': 3},
        3: {'name': 'Family',
            'plural_name': 'Families',
            'code': 'FM',
            'description': 'Caregivers of children ages 5-10',
            'default_text_difficulty': 1},
        2: {'name': 'Informal Educator',
            'plural_name': 'Informal Educators',
            'code': 'IE',
            'description': 'Educators of Grades K-12+ in out-of-school settings',
            'default_text_difficulty': 1},
        4: {'name': 'Student',
            'plural_name': 'Students',
            'code': 'ST',
            'description': 'Grades 6-12+',
            'default_text_difficulty': 1},
        1: {'name': 'Educator',
            'plural_name': 'Educators',
            'code': 'TE',
            'description': 'Educators of Grades K-12+ in school settings',
            'default_text_difficulty': 1},
    },
    'VALID_AUDIENCES': [1, 3, 4, ],
    'DEFAULT_AUDIENCE': 1,
}


try:
    from local_settings import *
except ImportError:
    pass
