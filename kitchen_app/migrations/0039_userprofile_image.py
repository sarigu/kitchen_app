# Generated by Django 3.1.3 on 2021-01-13 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0038_auto_20201214_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
