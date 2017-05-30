"""
This is an example settings/local.py file.
These settings overrides what's in settings/base.py
"""

from . import base


# To extend any settings from settings/base.py here's an example.
# If you don't need to extend any settings from base.py, you do not need
# to import base above
#INSTALLED_APPS = base.INSTALLED_APPS + ('django_nose',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'admin_lacaravane_new',
        'USER': 'lacaravane_user',
        'PASSWORD': 'O30@pw5j',
        'HOST': '',
        'PORT': '',
        #'OPTIONS': {
        #    'init_command': 'SET storage_engine=InnoDB',
        #    'charset' : 'utf8',
        #    'use_unicode' : True,
        #},
        #'TEST_CHARSET': 'utf8',
        #'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

# Recipients of traceback emails and other notifications.
ADMINS = (
    ('Dev', 'goppii.nath@gmail.com'),
)
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG404 = False
DEBUG = False
TEMPLATE_DEBUG = False

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = False

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
	'lacaravane.com',
	'www.lacaravane.com',
	'test.lacaravane.com'
]
#ALLOWED_HOSTS = ['*']

# SECURITY WARNING: keep the secret key used in production secret!
# Hardcoded values can leak through source control. Consider loading
# the secret key from an environment variable or a file instead.
SECRET_KEY = 't7^@1o@is33r035e8w8!eus@bvdv24$g5mq&-n&$4kjnjnt*5&'

# Uncomment these to activate and customize Celery:
# CELERY_ALWAYS_EAGER = False  # required to activate celeryd
# BROKER_HOST = 'localhost'
# BROKER_PORT = 5672
# BROKER_USER = 'django'
# BROKER_PASSWORD = 'django'
# BROKER_VHOST = 'django'
# CELERY_RESULT_BACKEND = 'amqp'

## Log settings

# Remove this configuration variable to use your custom logging configuration
#LOGGING_CONFIG = None


LOGGING = {
    'version': 1,
    'loggers': {
        'lacaravane': {
            'level': "DEBUG"
        }
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mysite.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'MYAPP': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}



	

#Placement is important. It's recommended to include this right after your < body > tag.

#{% load socialaccount %}
#{% providers_media_js %}

#To slim down to barebones settings for testing, you could also try this:

SOCIALACCOUNT_PROVIDERS = {
        'facebook':{
        'SCOPE': ['email', 'public_profile'],
        'METHOD': 'js_sdk',
    }
}

SITE_ID = 1

THUMBNAIL_DEBUG = False

PREPEND_WWW = True

INTERNAL_IPS = ('127.0.0.1')
