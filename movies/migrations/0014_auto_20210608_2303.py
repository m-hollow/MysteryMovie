# Generated by Django 3.1.2 on 2021-06-08 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0013_alltimescore_most_rounds_won'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alltimescore',
            old_name='date_last_run',
            new_name='date_created',
        ),
    ]
