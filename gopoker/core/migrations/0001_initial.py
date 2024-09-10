# Generated by Django 5.0.7 on 2024-09-10 23:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=6, null=True)),
                ('status', models.CharField(choices=[('O', 'Open'), ('X', 'Closed')], default='O', max_length=1)),
                ('game', models.CharField(choices=[('E', 'EMPTY'), ('BJ', 'Blackjack'), ('PK', 'Poker'), ('CR', 'Craps')], default='E', max_length=2)),
                ('host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hosted_room', to='core.player')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='core.room'),
        ),
    ]
