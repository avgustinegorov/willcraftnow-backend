import environ

env = environ.Env(
    # set casting, default value
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    EMAIL_MAIN=(str, False),
    EMAIL_HOST=(str, None),
    EMAIL_USE_TLS=(bool, False),
    EMAIL_PORT=(int, None),
    EMAIL_HOST_USER=(str, None),
    EMAIL_HOST_PASSWORD=(str, None),
)
# reading .env file
environ.Env.read_env()

SITE_ID = 1

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_MAIN = env("EMAIL_MAIN")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
