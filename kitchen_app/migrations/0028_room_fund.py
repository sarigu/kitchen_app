# Generated by Django 3.1.3 on 2020-12-13 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0027_room_mobilepaybox'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='fund',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]