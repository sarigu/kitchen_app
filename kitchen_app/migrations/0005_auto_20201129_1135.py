# Generated by Django 3.1.3 on 2020-11-29 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen_app', '0004_auto_20201127_1350'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roommembers',
            old_name='userID',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='roommembers',
            name='status',
            field=models.CharField(blank=True, choices=[('admin', 'Admin'), ('member', 'Member')], max_length=10, null=True),
        ),
    ]
