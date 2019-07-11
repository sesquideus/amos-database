# Generated by Django 2.2.3 on 2019-07-11 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0023_statusreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusreport',
            name='received',
            field=models.DateTimeField(auto_now_add=True, verbose_name='received at'),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='timestamp',
            field=models.DateTimeField(auto_now=True, verbose_name='timestamp'),
        ),
    ]
