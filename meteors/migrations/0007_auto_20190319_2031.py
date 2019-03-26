# Generated by Django 2.1.7 on 2019-03-19 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0006_auto_20190128_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at max light'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxLongitude',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude at max light'),
        ),
        migrations.AlterField(
            model_name='meteor',
            name='lightmaxTime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp at max light'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='angularSpeed',
            field=models.FloatField(blank=True, null=True, verbose_name='observed angular speed [°/s]'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='beginningAzimuth',
            field=models.FloatField(blank=True, null=True, verbose_name='azimuth at beginning'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='endAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at end'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='endAzimuth',
            field=models.FloatField(blank=True, null=True, verbose_name='azimuth at end'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='endTime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp at end'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='lightmaxAltitude',
            field=models.FloatField(blank=True, null=True, verbose_name='altitude at max light'),
        ),
    ]
