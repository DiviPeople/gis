"""Module indented for configuring the service via the environment variables. """

import os

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PG_DATABASE', 'cusdeb'),
        'USER': os.environ.get('PG_USER', 'postgres'),
        'PASSWORD': os.environ.get('PG_PASSWORD', 'secret'),
        'HOST': os.environ.get('PG_HOST', 'localhost'),
        'PORT': os.environ.get('PG_PORT', '54321'),
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'django_rest_passwordreset',

    'images',
    'users',
]

# Do not run anything if SECRET_KEY is not set.
SECRET_KEY = os.environ['SECRET_KEY']

CHECK_RUNNING_CONFIGURATION_ATTEMPTS = int(os.getenv('CHECK_RUNNING_CONFIGURATION_ATTEMPTS', '60'))

PORT = os.getenv('PORT', '8011')
