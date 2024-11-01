# Generated by Django 4.2.3 on 2024-02-20 23:11

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_rename_format_crmterm_type'),
        ('trafficdata', '0004_alter_trafficdata_adv_sub_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trafficdata',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trafficdata', to='settings.source', verbose_name='Source'),
        ),
    ]
