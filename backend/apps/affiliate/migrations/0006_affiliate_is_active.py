# Generated by Django 4.2.3 on 2024-01-29 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliate', '0005_remove_affiliate_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliate',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]