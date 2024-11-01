# Generated by Django 4.2.3 on 2023-07-25 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trafficdata', '0001_initial'),
        ('affiliate', '0002_initial'),
        ('settings', '0001_initial'),
        ('traffic_distribution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='executedrisk',
            name='trafficdata',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='executed_risk', to='trafficdata.trafficdata'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_logs', to='settings.event'),
        ),
        migrations.AddField(
            model_name='eventlog',
            name='trafficdata',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_logs', to='trafficdata.trafficdata'),
        ),
        migrations.AddField(
            model_name='eventdata',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_data', to='settings.event'),
        ),
        migrations.AddField(
            model_name='domain',
            name='affiliate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='affiliate.affiliate'),
        ),
        migrations.AddField(
            model_name='smsaffiliatefolder',
            name='affiliate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='affiliate.affiliate'),
        ),
        migrations.AddField(
            model_name='smsadvertiserfolder',
            name='advertiser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='traffic_distribution.advertiser'),
        ),
        migrations.AddField(
            model_name='riskmanagementaffiliatefolder',
            name='affiliate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='affiliate.affiliate'),
        ),
        migrations.AddField(
            model_name='riskmanagementadvertiserfolder',
            name='advertiser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='traffic_distribution.advertiser'),
        ),
        migrations.AddField(
            model_name='executedrisk',
            name='risk_folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='executed_risks', to='settings.riskfolder'),
        ),
    ]
