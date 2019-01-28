# Generated by Django 2.1.5 on 2019-01-28 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0015_auto_20190128_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='timezone',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stations.TimeZone'),
        ),
    ]
