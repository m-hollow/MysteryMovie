# Generated by Django 3.1.2 on 2020-10-29 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_userprofile_rounds_won'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='total_disliked_movie_points',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_liked_movie_points',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userrounddetail',
            name='disliked_movie_points',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userrounddetail',
            name='finalized_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userrounddetail',
            name='liked_movie_points',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
    ]