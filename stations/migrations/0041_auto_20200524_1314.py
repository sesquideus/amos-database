# Generated by Django 3.0.5 on 2020-05-24 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0040_station_on'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StatusReport',
            new_name='Heartbeat',
        ),
        migrations.RemoveIndex(
            model_name='heartbeat',
            name='stations_st_timesta_83cb25_idx',
        ),
        migrations.AddIndex(
            model_name='heartbeat',
            index=models.Index(fields=['timestamp', 'station'], name='stations_he_timesta_db3c36_idx'),
        ),
    ]
