# Generated by Django 3.1.3 on 2020-12-05 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0015_comments_posts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='room',
        ),
    ]
