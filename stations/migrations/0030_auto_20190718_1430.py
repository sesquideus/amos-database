# Generated by Django 2.2.3 on 2019-07-18 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0029_auto_20190718_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='stations/'),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='heating',
            field=models.CharField(blank=True, choices=[('1', 'on'), ('0', 'off'), ('P', 'problem')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='lid',
            field=models.CharField(blank=True, choices=[('O', 'open'), ('C', 'closed'), ('P', 'problem')], max_length=1, null=True),
        ),
    ]