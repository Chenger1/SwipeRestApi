# Generated by Django 3.2.5 on 2021-07-25 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_db', '0046_auto_20210725_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customabstractuser',
            name='email',
            field=models.CharField(blank=True, help_text='150 characters max. Available symbols: aA-wW, [0-9], @ . _', max_length=150, null=True, unique=True, verbose_name='email'),
        ),
    ]
