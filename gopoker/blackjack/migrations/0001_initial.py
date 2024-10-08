# Generated by Django 5.0.7 on 2024-09-10 23:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackjackRoom',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.room')),
                ('deck', models.JSONField(default=list)),
                ('dealer_score', models.IntegerField(default=0)),
            ],
            bases=('core.room',),
        ),
        migrations.CreateModel(
            name='BlackjackPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chips', models.IntegerField(default=0)),
                ('has_blackjack', models.BooleanField(default=False)),
                ('current_hand_value', models.IntegerField(default=0)),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blackjack_player', to='core.player')),
            ],
        ),
    ]
