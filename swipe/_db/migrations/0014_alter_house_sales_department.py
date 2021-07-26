# Generated by Django 3.2.5 on 2021-07-12 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0013_user_ban'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='sales_department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_houses', to='_db.user'),
        ),
    ]
