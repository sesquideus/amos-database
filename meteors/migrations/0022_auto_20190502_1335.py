# Generated by Django 2.2 on 2019-05-02 13:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0021_meteor_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frame',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=False,
        ),
    ]
