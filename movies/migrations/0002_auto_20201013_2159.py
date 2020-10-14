# Generated by Django 3.1.2 on 2020-10-13 21:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='chosen_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chosen_movie', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='movie',
            name='watched',
            field=models.BooleanField(default=False),
        ),
    ]
