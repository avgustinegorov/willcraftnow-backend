import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SSL=(bool, False),
)
# reading .env file
environ.Env.read_env()

if env("SSL"):
    # SSL
    CORS_REPLACE_HTTPS_REFERER = True
    HOST_SCHEME = "https://"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 1000000
    SECURE_FRAME_DENY = True
