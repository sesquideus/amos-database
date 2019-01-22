# Generated by Django 2.1.5 on 2019-01-22 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0004_auto_20190113_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='magnitude',
            field=models.FloatField(blank=True, null=True, verbose_name='apparent magnitude'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='station',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stations.Station', verbose_name='station'),
        ),
    ]
