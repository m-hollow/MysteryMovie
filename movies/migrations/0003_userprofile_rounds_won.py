# Generated by Django 3.1.2 on 2020-10-24 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_auto_20201023_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rounds_won',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
