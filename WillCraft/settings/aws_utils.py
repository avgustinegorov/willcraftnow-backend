from storages.backends.s3boto3 import S3Boto3Storage
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()


class StaticRootS3BotoStorage(S3Boto3Storage):
    location = "static"
    bucket_name = env("STATIC_AWS_STORAGE_BUCKET_NAME")


class MediaRootS3BotoStorage(S3Boto3Storage):
    location = "media"
    bucket_name = env("MEDIA_AWS_STORAGE_BUCKET_NAME")
