# Generated by Django 3.0.5 on 2020-07-25 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0041_auto_20200524_1314'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='heartbeat',
            options={'get_latest_by': ['timestamp'], 'ordering': ['-timestamp'], 'verbose_name': 'heartbeat report', 'verbose_name_plural': 'heartbeat reports'},
        ),
        migrations.AlterField(
            model_name='heartbeat',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heartbeats', to='stations.Station'),
        ),
    ]
