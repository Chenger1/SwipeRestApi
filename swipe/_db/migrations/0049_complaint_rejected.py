# Generated by Django 3.2.5 on 2021-07-26 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0048_auto_20210726_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]
