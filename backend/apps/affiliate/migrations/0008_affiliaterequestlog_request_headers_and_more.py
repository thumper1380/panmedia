# Generated by Django 4.2.3 on 2024-02-20 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('affiliate', '0007_alter_affiliate_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliaterequestlog',
            name='request_headers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='apitoken',
            name='affiliate',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='api_tokens', to='affiliate.affiliate'),
        ),
        migrations.AlterField(
            model_name='apitoken',
            name='email_validation',
            field=models.BooleanField(default=False, help_text="Whether to validate the lead's email", verbose_name='Email Validation'),
        ),
        migrations.AlterField(
            model_name='apitoken',
            name='phone_validation',
            field=models.BooleanField(default=False, help_text="Whether to validate the lead's phone number", verbose_name='Phone Validation'),
        ),
    ]
