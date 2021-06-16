import boto3
import re
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from billing.models import Invoice, InvoiceRepo


INVOICE_FILE_NAME_RE = re.compile(r"^(.+)_v(\d+)\.pdf$", re.IGNORECASE)
INVOICE_FILE_NAME_2_RE = re.compile(r"^(.+)\.pdf$", re.IGNORECASE)


class Command(BaseCommand):  # pragma: no cover
    help = "Fix invoice repo entries and files versioning"

    def handle(self, *args, **options):
        s3_client = None
        invoices = Invoice.objects.filter(invoice_repo__isnull=False)
        for invoice in invoices:
            for i, repo in enumerate(invoice.invoice_repo.order_by("version"), 1):

                old_name = repo.invoice_pdf.name
                new_name = None

                match = INVOICE_FILE_NAME_RE.match(old_name)
                if match:
                    new_name = f"{match.group(1)}_v{i}.pdf"
                else:
                    match = INVOICE_FILE_NAME_2_RE.match(old_name)
                    if match:
                        new_name = f"{match.group(1)}_v{i}.pdf"

                if new_name and new_name != old_name:
                    self.stdout.write(
                        self.style.SUCCESS(f"RENAMING {old_name} TO {new_name}")
                    )
                    if (
                        settings.DEFAULT_FILE_STORAGE
                        == "django.core.files.storage.FileSystemStorage"
                    ):
                        initial_path = repo.invoice_pdf.path
                        repo.invoice_pdf.name = new_name
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                        os.rename(initial_path, new_path)
                    elif (
                        settings.DEFAULT_FILE_STORAGE
                        == "WillCraft.settings.aws_utils.MediaRootS3BotoStorage"
                    ):
                        if not s3_client:
                            s3_client = boto3.client(
                                "s3",
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                region_name=settings.S3DIRECT_REGION,
                            )

                        repo.invoice_pdf.name = new_name

                        # In S3, there is no rename_object command:
                        #   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
                        # Therefore, we need to emulate rename with copy + delete.
                        s3_client.copy_object(
                            Bucket=settings.MEDIA_AWS_STORAGE_BUCKET_NAME,
                            Key=f"media/{new_name}",
                            CopySource=dict(
                                Bucket=settings.MEDIA_AWS_STORAGE_BUCKET_NAME,
                                Key=f"media/{old_name}",
                            ),
                        )
                        s3_client.delete_object(
                            Bucket=settings.MEDIA_AWS_STORAGE_BUCKET_NAME,
                            Key=f"media/{old_name}",
                        )

                repo.version = i
                repo.save()
