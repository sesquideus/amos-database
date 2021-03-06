# Generated by Django 2.1.5 on 2019-01-28 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0005_auto_20190122_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sighting',
            name='beginningElevation',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='endElevation',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='lightmaxElevation',
        ),
        migrations.AddField(
            model_name='sighting',
            name='beginningAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at beginning'),
        ),
        migrations.AddField(
            model_name='sighting',
            name='endAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at beginning'),
        ),
        migrations.AddField(
            model_name='sighting',
            name='lightmaxAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='elevation at max light'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at maxlight'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxLatitude',
            field=models.FloatField(blank=True, null=True, verbose_name='latitude at max light'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxLongitude',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude at maxlight'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxTime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp at maxlight'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='beginningAzimuth',
            field=models.FloatField(blank=True, null=True, verbose_name='elevation at beginning'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='lightmaxAzimuth',
            field=models.FloatField(blank=True, null=True, verbose_name='azimuth at max light'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='lightmaxTime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp at max light'),
        ),
    ]
