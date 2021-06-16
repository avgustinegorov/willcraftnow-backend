"""
Django settings for WillCraft project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "NOT SET"),
    STAGE=(str, "LOCAL"),
)
# reading .env file
environ.Env.read_env()

SITE_ID = 1

STAGE = env("STAGE")

ADMINS = [("Admin Error Report", "admin@willcraftnow.com")]

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# Contains all of the files that may be required during unit tests
TEST_FILES_DIR = os.path.join(BASE_DIR, "test_files")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "storages",
    "services",
    "django_countries",
    "import_export",
    # script dependency
    "django_extensions",
    # applications
    "history",
    "lambda_service",
    "lawyer_services",
    "persons",
    "lastrites",
    "willcraft_auth",
    "assets",
    "billing",
    "core",
    "content",
    "partners",
    "powers",
    # 'silk',
    # rest api dependencies
    "rest_framework",
    # Auth Dependencies
    "oauth2_provider",
    "rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_auth.registration",
    # react Dependencies
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsPostCsrfMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "WillCraft.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"), ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "WillCraft.wsgi.application"