# Generated by Django 3.1.3 on 2020-12-04 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0012_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='type',
            field=models.CharField(choices=[('getTogether', 'GetTogether'), ('kitchenMeeting', 'KitchenMeeting'), ('kitchenCleaning', 'kitchenCleaning')], default='getTogether', max_length=20),
        ),
    ]