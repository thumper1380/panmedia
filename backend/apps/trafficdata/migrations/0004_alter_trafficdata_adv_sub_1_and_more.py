# Generated by Django 4.2.3 on 2024-01-29 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trafficdata', '0003_alter_trafficdata_advertiser_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trafficdata',
            name='adv_sub_1',
            field=models.CharField(blank=True, max_length=50, verbose_name='Adv Sub 1'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='adv_sub_2',
            field=models.CharField(blank=True, max_length=50, verbose_name='Adv Sub 2'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='adv_sub_3',
            field=models.CharField(blank=True, max_length=50, verbose_name='Adv Sub 3'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='adv_sub_4',
            field=models.CharField(blank=True, max_length=50, verbose_name='Adv Sub 4'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='adv_sub_5',
            field=models.CharField(blank=True, max_length=50, verbose_name='Adv Sub 5'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 1'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_10',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 10'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_11',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 11'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_12',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 12'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_13',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 13'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_14',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 14'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_15',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 15'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_16',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 16'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_17',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 17'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_18',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 18'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_19',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 19'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 2'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_20',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 20'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_3',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 3'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_4',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 4'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_5',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 5'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_6',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 6'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_7',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 7'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_8',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 8'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='aff_sub_9',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aff Sub 9'),
        ),
        migrations.AlterField(
            model_name='trafficdata',
            name='is_risky',
            field=models.BooleanField(default=False, verbose_name='Risky'),
        ),
    ]
