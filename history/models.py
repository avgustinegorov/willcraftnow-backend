from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


class ChangeEvent(models.Model):
    """A Model connected to multiple Models
    through pre-save signals
    for the purpose of storing their individual
    change history
    """

    CHANGE_TYPES = [
        ("UPDATE", "Update",),
        ("CREATE", "Create"),
        ("DELETE", "Delete",),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    # Contains the type of change - from CHANGE_TYPES
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES, blank=False)

    # This contains a dictionary of fields that were changed or is empty
    # -> If no fields were changed (delete/create)
    changes = models.TextField(blank=True)

    # The item that the change event was fired on
    content_type = models.ForeignKey(
        ContentType, null=False, on_delete=models.CASCADE
    )  # The changed model's class

    object_id = models.PositiveIntegerField(null=False)  # The changed model's PK
    # The instance that contentTypes will select for us based on the above two fields
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):  # pragma: no cover
        return f"{self.change_type} - {self.content_type.model}"
