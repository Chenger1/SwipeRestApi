# Generated by Django 3.2.5 on 2021-07-16 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0023_rename_owner_flat_owned'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postimage',
            name='name',
        ),
    ]
