# Generated by Django 5.1 on 2024-09-11 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokerplayer',
            name='stack',
            field=models.IntegerField(default=0),
        ),
    ]