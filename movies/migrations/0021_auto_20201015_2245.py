# Generated by Django 3.1.2 on 2020-10-15 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0020_auto_20201015_2213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameround',
            old_name='current_round',
            new_name='active_round',
        ),
        migrations.AddField(
            model_name='gameround',
            name='round_completed',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Round Already Completed'),
        ),
    ]
