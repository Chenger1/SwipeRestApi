# Generated by Django 3.2.5 on 2021-07-19 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0039_alter_promotion_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='end_date',
            field=models.DateField(blank=True),
        ),
    ]
