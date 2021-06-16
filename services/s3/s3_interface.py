""" Contains an S3Interface object that provides all required methods
	to work directly with the S3 environment
"""

import boto3
from django.conf import settings


class S3Interface:
    """An Object implementing all methods required to
    work directly with the S3 Environment
    """

    def generate_s3_client(self):
        """ Generates and returns an s3 client with the credentials in settings """
        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        client = session.client(
            "s3",
            settings.S3DIRECT_REGION,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        return client

    def get_put_presigned_url(self, file_name):
        """ Returns a Presigned PUT_OBJECT Url for the given filename """
        client = self.generate_s3_client()

        return client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": settings.MEDIA_AWS_STORAGE_BUCKET_NAME,
                    "Key": file_name},
        )

    def get_download_presigned_url(self, file_name):
        """ Returns a Presigned PUT_OBJECT Url for the given filename """
        client = self.generate_s3_client()

        return client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.MEDIA_AWS_STORAGE_BUCKET_NAME,
                    "Key": file_name},
        )
