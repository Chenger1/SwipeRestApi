# Generated by Django 3.2.5 on 2021-08-09 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0051_userfilter_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='name',
        ),
        migrations.RemoveField(
            model_name='floor',
            name='name',
        ),
        migrations.RemoveField(
            model_name='section',
            name='name',
        ),
        migrations.AddField(
            model_name='building',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='floor',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
