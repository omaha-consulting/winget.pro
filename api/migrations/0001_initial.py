# Generated by Django 4.0 on 2021-12-10 09:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=128, unique=True)),
                ('name', models.CharField(max_length=256, validators=[django.core.validators.MinLengthValidator(2)])),
                ('publisher', models.CharField(max_length=256, validators=[django.core.validators.MinLengthValidator(2)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.package')),
            ],
        ),
        migrations.CreateModel(
            name='Installer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('architecture', models.CharField(choices=[('x86', 'x86'), ('x64', 'x64'), ('arm', 'arm'), ('arm64', 'arm64')], max_length=5)),
                ('type', models.CharField(choices=[('msix', 'msix'), ('msi', 'msi'), ('appx', 'appx'), ('exe', 'exe'), ('zip', 'zip'), ('inno', 'inno'), ('nullsoft', 'nullsoft'), ('wix', 'wix'), ('burn', 'burn'), ('pwa', 'pwa'), ('msstore', 'msstore')], max_length=8)),
                ('url', models.URLField()),
                ('sha256', models.CharField(max_length=64, validators=[django.core.validators.RegexValidator('^[a-fA-F0-9]{64}$')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.version')),
            ],
        ),
    ]
