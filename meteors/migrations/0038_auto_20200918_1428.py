# Generated by Django 3.1.1 on 2020-09-18 14:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0037_auto_20200804_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meteor',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.utcnow, verbose_name='timestamp'),
        ),
    ]