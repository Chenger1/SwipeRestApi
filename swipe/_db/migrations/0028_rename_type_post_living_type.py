# Generated by Django 3.2.5 on 2021-07-16 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0027_post_main_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='type',
            new_name='living_type',
        ),
    ]
