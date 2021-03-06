# Generated by Django 3.1.3 on 2021-01-25 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0041_sighting_avi_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='avi_size',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='AVI file size'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='jpg',
            field=models.ImageField(blank=True, null=True, upload_to='sightings/%Y/%m/%d/', verbose_name='JPG composite'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='xml',
            field=models.FileField(blank=True, null=True, upload_to='sightings/%Y/%m/%d/', verbose_name='XML file'),
        ),
    ]
