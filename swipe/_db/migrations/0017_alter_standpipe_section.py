# Generated by Django 3.2.5 on 2021-07-13 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0016_alter_standpipe_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standpipe',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipes', to='_db.section'),
        ),
    ]
