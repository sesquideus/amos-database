# Generated by Django 2.2.3 on 2019-07-11 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0021_subnetwork_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subnetwork',
            name='code',
            field=models.CharField(help_text='a simple unique code (2-4 uppercase letters)', max_length=8, unique=True),
        ),
    ]