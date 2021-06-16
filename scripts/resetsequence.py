from core.models import WillRepo
from django.core.management.color import no_style
from django.db import connection


def run():
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [WillRepo])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
