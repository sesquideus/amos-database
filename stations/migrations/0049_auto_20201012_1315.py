# Generated by Django 3.1.1 on 2020-10-12 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0048_auto_20201005_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='heartbeat',
            name='storage_permanent_available',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='heartbeat',
            name='storage_permanent_total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='heartbeat',
            name='storage_primary_available',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='heartbeat',
            name='storage_primary_total',
            field=models.FloatField(blank=True, null=True),
        ),
    ]