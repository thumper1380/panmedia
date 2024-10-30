# Generated by Django 4.2.3 on 2023-12-14 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webauth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebAuthDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='nickname to help the user identify a given key', max_length=250)),
                ('credential_id', models.BinaryField(max_length=128)),
                ('public_key', models.BinaryField(max_length=256)),
                ('format', models.CharField(help_text='generated by the client authenticator to identify this key', max_length=250)),
                ('type', models.CharField(max_length=250)),
                ('sign_count', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webauth_devices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]