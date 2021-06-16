import os

import dj_database_url
import environ

from .base import BASE_DIR

env = environ.Env(
    # set casting, default value
    SQL_ENGINE=(str, "django.db.backends.sqlite3"),
    SQL_DATABASE=(str, os.path.join(BASE_DIR, "db.sqlite3")),
    SQL_USER=(str, None),
    SQL_PASSWORD=(str, None),
    SQL_HOST=(str, None),
    SQL_PORT=(str, None),
    DATABASE_URL=(str, None),
)

# reading .env file
environ.Env.read_env()

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


if env("DATABASE_URL"):
    # overrides default database to use heroku
    db_from_env = dj_database_url.config()
    DATABASES = {"default": {}}
    DATABASES["default"].update(db_from_env)
    DATABASES["default"]["CONN_MAX_AGE"] = 500

else:

    DATABASES = {
        "default": {
            "ENGINE": env("SQL_ENGINE"),
            "NAME": env("SQL_DATABASE"),
            "USER": env("SQL_USER"),
            "PASSWORD": env("SQL_PASSWORD"),
            "HOST": env("SQL_HOST"),
            "PORT": env("SQL_PORT"),
        }
    }
