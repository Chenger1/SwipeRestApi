# Generated by Django 3.2.5 on 2021-07-16 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0024_remove_postimage_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='house',
        ),
        migrations.AddField(
            model_name='post',
            name='flat',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='_db.flat'),
            preserve_default=False,
        ),
    ]
