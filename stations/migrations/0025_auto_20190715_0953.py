# Generated by Django 2.2.3 on 2019-07-15 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0024_auto_20190711_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusreport',
            name='timestamp',
            field=models.DateTimeField(verbose_name='timestamp'),
        ),
    ]