# Generated by Django 5.1 on 2024-09-23 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0004_pokerplayer_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokerplayer',
            name='buyin',
            field=models.IntegerField(default=0),
        ),
    ]
