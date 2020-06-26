# Generated by Django 2.2.7 on 2019-11-19 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0029_auto_20191113_1531'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meteor',
            old_name='beginningAltitude',
            new_name='beginning_altitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='beginningLatitude',
            new_name='beginning_latitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='beginningLongitude',
            new_name='beginning_longitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='beginningTime',
            new_name='beginning_time',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='endAltitude',
            new_name='end_altitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='endLatitude',
            new_name='end_latitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='endLongitude',
            new_name='end_longitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='endTime',
            new_name='end_time',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='lightmaxAltitude',
            new_name='lightmax_altitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='lightmaxLatitude',
            new_name='lightmax_latitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='lightmaxLongitude',
            new_name='lightmax_longitude',
        ),
        migrations.RenameField(
            model_name='meteor',
            old_name='lightmaxTime',
            new_name='lightmax_time',
        ),
    ]