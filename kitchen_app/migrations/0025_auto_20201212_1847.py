# Generated by Django 3.1.3 on 2020-12-12 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0024_rules'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rules',
            old_name='updated',
            new_name='updated_at',
        ),
    ]
