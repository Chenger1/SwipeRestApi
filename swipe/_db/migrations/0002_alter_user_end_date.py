# Generated by Django 3.2.5 on 2021-07-05 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
