# Generated by Django 3.2.5 on 2021-07-16 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0022_flat_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flat',
            old_name='owner',
            new_name='owned',
        ),
    ]
