# Generated by Django 3.1.3 on 2020-12-05 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0017_auto_20201205_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='room',
        ),
        migrations.AlterField(
            model_name='comments',
            name='text',
            field=models.CharField(max_length=250),
        ),
    ]