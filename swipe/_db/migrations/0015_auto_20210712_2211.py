# Generated by Django 3.2.5 on 2021-07-12 19:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0014_alter_house_sales_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to='media/documents'),
        ),
        migrations.AlterField(
            model_name='flat',
            name='schema',
            field=models.ImageField(upload_to='media/flats/schema'),
        ),
        migrations.AlterField(
            model_name='flat',
            name='schema_in_house',
            field=models.ImageField(upload_to='media/flats/schema_in_house'),
        ),
        migrations.AlterField(
            model_name='house',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/houses'),
        ),
        migrations.AlterField(
            model_name='house',
            name='sales_department',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='managed_houses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='postimage',
            name='image',
            field=models.ImageField(upload_to='media/posts'),
        ),
    ]