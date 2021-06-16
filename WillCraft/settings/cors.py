import environ

env = environ.Env(
    # set casting, default value
    ALLOWED_HOSTS=(list, ["*"]),
    CORS_ORIGIN_WHITELIST=(list, ["*"]),
    CSRF_TRUSTED_ORIGINS=(list, ["*"]),
    CORS_ORIGIN_ALLOW_ALL=(bool, True),
)
# reading .env file
environ.Env.read_env()

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CORS_ORIGIN_WHITELIST = env.list("CSRF_TRUSTED_ORIGINS")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL")
