# Generated by Django 2.1.5 on 2019-01-15 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0009_auto_20190113_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='address',
            field=models.CharField(blank=True, help_text='Printable full address', max_length=256, null=True),
        ),
    ]