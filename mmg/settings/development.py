"""
Django settings for mmg project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import environ
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, True)
)

environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# IMPORTANT!
# NOTE: I had to add one additional .parent to the line below, because I moved this settings file (development.py)
# into a new folder, 'settings'. BASE_DIR is set relative to the path where this file exists; by default,
# it expects to go back two levels, so the final dir in the path is the primary project folder, e.g. MMG.
# but since I have manually changed the location of the settings file and nested it one level deeper, we have
# to set this relatively by adding one more .parent --if you don't do this, the BASE_DIR path ends at MMG/mmg instead of
# at MMG
# the relative path goes like this:   development.py > to first parent > settings > to second parent > mmg (dir)
# but then when the static files get created, they are screwed up
# NOTE: you'll need to do this in the production.py file as well! since it is also nested one level deeper

# Summary: when you change the location of the settings file used by django, you are also changing the path
# stored in BASE_DIR, because this path is assigned *relative to where the settings file is stored*.

# my solution could conceivably have side effects, so remember that this change was made...

BASE_DIR = Path(__file__).resolve().parent.parent.parent   # see above explanations. django default of this line
                                                           # has two (2) .parent total; I have added a third

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My apps
    'movies.apps.MoviesConfig',
    'users.apps.UsersConfig',

    # Third Party apps
    'bootstrap4',
    'crispy_forms',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mmg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mmg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures')]     # added by me

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]  # static files in local development
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     # static files in production
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# My settings
LOGIN_URL = 'login'   # used by django to redirect to login when @login_required gets unauthorized access

LOGIN_REDIRECT_URL = 'movies:index'   # same as below
LOGOUT_REDIRECT_URL = 'login'  # using this now because using 'next' was messing up w/ sessions variable

