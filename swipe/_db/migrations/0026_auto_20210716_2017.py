# Generated by Django 3.2.5 on 2021-07-16 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0025_auto_20210716_1421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='address',
        ),
        migrations.RemoveField(
            model_name='post',
            name='balcony',
        ),
        migrations.RemoveField(
            model_name='post',
            name='foundation_doc',
        ),
        migrations.RemoveField(
            model_name='post',
            name='heating',
        ),
        migrations.RemoveField(
            model_name='post',
            name='kitchen_square',
        ),
        migrations.RemoveField(
            model_name='post',
            name='number_of_rooms',
        ),
        migrations.RemoveField(
            model_name='post',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='post',
            name='square',
        ),
        migrations.RemoveField(
            model_name='post',
            name='state',
        ),
        migrations.AddField(
            model_name='flat',
            name='heating',
            field=models.CharField(choices=[('NO', 'Нет'), ('CENTER', 'Центральное'), ('PERSONAL', 'Индивидуальное')], default='NO', max_length=8),
        ),
    ]