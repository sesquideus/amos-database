# Generated by Django 3.0.4 on 2020-04-17 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0037_subnetwork_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusreport',
            name='status',
            field=models.CharField(blank=True, choices=[('O', 'observing'), ('M', 'malfunction'), ('N', 'not observing')], max_length=1, null=True),
        ),
    ]
