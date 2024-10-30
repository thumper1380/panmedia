# Generated by Django 4.2.3 on 2024-02-21 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliate', '0008_affiliaterequestlog_request_headers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apitoken',
            name='is_enabled',
        ),
        migrations.AddField(
            model_name='apitoken',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Enabled'),
        ),
    ]