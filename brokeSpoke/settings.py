"""
Django settings for brokeSpoke project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from json import load
import os
import subprocess
import dj_database_url
import psycopg2

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rr_-rk#1kic_wac6q+zft^_@zuf1f4av4)5fxx^zkcj&vwa4jz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['fast-plateau-15716.herokuapp.com','127.0.0.1','localhost','portal.brokespoke.org']


# Application definition

INSTALLED_APPS = [
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard.apps.DashboardConfig',
    'crispy_forms',
    'bootstrap3_datetime',
    'tempus_dominus',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'brokeSpoke.urls'

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

WSGI_APPLICATION = 'brokeSpoke.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'brokespokedb',
#         'USER': 'willshapiro',
#         'PASSWORD':'Packrat1@',
#         'HOST':'localhost',
#         'PORT':'5432'
#     }
# }
# os.system("echo here is the heroku config")
# DATABASE_URL= subprocess.check_output("heroku config:get DATABASE_URL",shell=True,text=True)
# print(f"this is the db url {DATABASE_URL}")
# DATABASES = {}
# DATABASES['default'] = dj_database_url.config(default=str(DATABASE_URL))
# DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'brokespoke',
        'USER': 'postgres',
        'PASSWORD':'',
        'HOST':'127.0.0.1',
        'PORT':'5432'
    }
}


# uncomment this for prod
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_L10N = False

USE_TZ = False

TEMPUS_DOMINUS_INCLUDE_ASSETS = True
TEMPUS_DOMINUS_LOCALIZE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "dashboard/static"),
#     # '/var/www/static/',
# ]
STATIC_ROOT = os.path.join(BASE_DIR, "dashboard/static")
STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "dashboard/static")]
MEDIA_ROOT =  os.path.join(BASE_DIR, 'media') 
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/'