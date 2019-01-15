# Generated by Django 2.1.5 on 2019-01-12 22:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meteors', '0003_remove_sighting_observer'),
        ('stations', '0004_station_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'log entries',
                'verbose_name': 'log entry',
            },
        ),
        migrations.DeleteModel(
            name='Observer',
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='station',
            name='name',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AddField(
            model_name='logentry',
            name='station',
            field=models.ForeignKey(blank=True, help_text='the station in question', null=True, on_delete=django.db.models.deletion.CASCADE, to='stations.Station', verbose_name='station'),
        ),
    ]