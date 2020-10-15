# Generated by Django 3.1.2 on 2020-10-14 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_auto_20201014_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermoviedetail',
            name='star_rating',
            field=models.PositiveSmallIntegerField(choices=[(1, 'There is no coming back from this, it has destroyed me...(One Star)'), (2, 'New dimensions of suffering were learned...(Two Stars)'), (3, 'Damage sustained, but I will recover...(Three Stars)'), (4, 'Rather light on hurting, actually...(Four Stars)'), (5, "Wow, it didn't hurt at all!!...(Five Stars)")], default=3, verbose_name='Deep Hurting Level'),
        ),
    ]
