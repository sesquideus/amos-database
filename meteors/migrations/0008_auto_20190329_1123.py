# Generated by Django 2.1.7 on 2019-03-29 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0007_auto_20190319_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videoframe',
            name='sighting',
        ),
        migrations.AlterModelOptions(
            name='meteor',
            options={'ordering': ['lightmaxTime'], 'verbose_name': 'meteor'},
        ),
        migrations.RemoveField(
            model_name='meteor',
            name='timestamp',
        ),
        migrations.DeleteModel(
            name='VideoFrame',
        ),
    ]