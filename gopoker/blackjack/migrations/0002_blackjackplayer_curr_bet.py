# Generated by Django 5.0.7 on 2024-10-14 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blackjack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blackjackplayer',
            name='curr_bet',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]