# Generated by Django 2.2 on 2021-04-10 23:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lawyer_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='firm',
            name='lawyers',
            field=models.ManyToManyField(blank=True, null=True, related_name='lawyers', to=settings.AUTH_USER_MODEL),
        ),
    ]