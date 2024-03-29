# Generated by Django 3.2.10 on 2023-08-03 10:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0003_migrate_existing_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='user',
        ),
        migrations.AlterField(
            model_name='tenant',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
