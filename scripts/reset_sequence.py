from django.core.management.color import no_style
from django.db import connection
from django.utils import timezone

from persons.models import Beneficiary, PersonalDetails


def run(*args):
    sequence_sql = connection.ops.sequence_reset_sql(
        no_style(), [Beneficiary, PersonalDetails]
    )
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
