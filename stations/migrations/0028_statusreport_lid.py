# Generated by Django 2.2.3 on 2019-07-18 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0027_auto_20190717_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusreport',
            name='lid',
            field=models.CharField(choices=[('O', 'Open'), ('C', 'Closed'), ('P', 'Problem')], default='C', max_length=1),
            preserve_default=False,
        ),
    ]
