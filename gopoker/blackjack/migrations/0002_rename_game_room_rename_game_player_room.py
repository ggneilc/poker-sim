# Generated by Django 5.0.6 on 2024-07-30 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blackjack', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Game',
            new_name='Room',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='game',
            new_name='room',
        ),
    ]
