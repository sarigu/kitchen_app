# Generated by Django 3.1.3 on 2020-12-14 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0037_auto_20201214_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
