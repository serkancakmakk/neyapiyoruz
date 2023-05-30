"""
Django settings for etkinlik project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cstqf^z!#b#ulbu*jddwv&ps2$i#58a((+&l282tz!6#i*htqn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition


INSTALLED_APPS = [
    'ckeditor_uploader',
    'ckeditor',
    'cities_light',
    'haydi',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'etkinlik.urls'

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

WSGI_APPLICATION = 'etkinlik.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'etkinlik', 'static'),
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike', 'BulletedList', 'NumberedList', 'Indent', 'Outdent'],
            ['Link', 'Unlink', 'Table', 'Blockquote', 'CodeSnippet', 'TextColor', 'BGColor'],
            ['Undo', 'Redo'],
            ['Source'],
        ],
        'format_tags': 'p;h1;h2;h3;h4;h5;h6',
        'removePlugins': 'image',
        'extraAllowedContent': 'span;ul;li;table;td;style',
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# CİTİES LİGHT AYARLARI
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['tr']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['TR']
CITIES_LIGHT_COUNTRY_CODES = ['TR']  # Sadece Türkiye verilerini indirir
import locale

locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['tr']  # Türkçe dilini ekleyin
CITIES_LIGHT_TIMEZONES = ['UTC']
