import environ

env = environ.Env(
    # set casting, default value
    GA_TRACKING_ID=(str, "NOT SET"),
    FACEBOOK_TRACKING_ID=(str, "NOT SET"),
    TRACKING_DEBUG=(bool, False),
)
# reading .env file
environ.Env.read_env()

GA_TRACKING_ID = env("GA_TRACKING_ID")
FACEBOOK_TRACKING_ID = env("FACEBOOK_TRACKING_ID")
TRACKING_DEBUG = env.bool("TRACKING_DEBUG")
