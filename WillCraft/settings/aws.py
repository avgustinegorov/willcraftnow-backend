import datetime
import environ
import os
from .static import STATICFILES_DIRS

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = True

DEFAULT_FILE_STORAGE = "WillCraft.settings.aws_utils.MediaRootS3BotoStorage"
STATICFILES_STORAGE = "WillCraft.settings.aws_utils.StaticRootS3BotoStorage"

STATIC_AWS_STORAGE_BUCKET_NAME = env("STATIC_AWS_STORAGE_BUCKET_NAME")
MEDIA_AWS_STORAGE_BUCKET_NAME = env("MEDIA_AWS_STORAGE_BUCKET_NAME")
S3DIRECT_REGION = "ap-southeast-1"

MEDIA_URL = "https://%s.s3.amazonaws.com/media/" % MEDIA_AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL

STATIC_URL = "https://%s.s3.amazonaws.com/static/" % STATIC_AWS_STORAGE_BUCKET_NAME
STATIC_ROOT = STATIC_URL

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

AWS_IS_GZIPPED = True
AWS_DEFAULT_ACL = None

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    "Expires": expires,
    "Cache-Control": "max-age=%d" % (int(two_months.total_seconds()),),
}
