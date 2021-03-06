# Generated by Django 3.1.1 on 2020-11-09 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0051_auto_20201109_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heartbeat',
            name='cover_state',
            field=models.CharField(blank=True, choices=[('O', 'open'), ('o', 'opening'), ('C', 'closed'), ('c', 'closing'), ('P', 'problem'), ('S', 'safety')], max_length=1, null=True),
        ),
    ]
