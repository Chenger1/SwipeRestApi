# Generated by Django 3.2.5 on 2021-07-11 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0011_attachment_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/users/'),
        ),
    ]
