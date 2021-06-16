import environ
from .base import INSTALLED_APPS, MIDDLEWARE

env = environ.Env(
    # set casting, default value
    SILK=(bool, "False"),
    SILKY_PYTHON_PROFILER=(bool, "False"),
)
# reading .env file
environ.Env.read_env()

SILK = env("SILK")
SILKY_PYTHON_PROFILER = env("SILKY_PYTHON_PROFILER")

if env("SILK"):

    MIDDLEWARE.insert(2, "silk.middleware.SilkyMiddleware")

    INSTALLED_APPS += ["silk"]
