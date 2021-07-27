# Generated by Django 3.2.5 on 2021-07-08 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0005_auto_20210708_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promotions', to='_db.promotiontype'),
        ),
        migrations.AlterField(
            model_name='house',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media'),
        ),
    ]