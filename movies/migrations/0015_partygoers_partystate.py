# Generated by Django 4.2.16 on 2024-11-04 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0014_auto_20210608_2303'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartyGoers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.PositiveSmallIntegerField()),
                ('last_ping', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PartyState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx', models.PositiveSmallIntegerField()),
                ('next_time', models.DateTimeField()),
            ],
        ),
    ]