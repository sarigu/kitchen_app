# Generated by Django 3.1.3 on 2020-11-30 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0008_auto_20201129_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasks',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
