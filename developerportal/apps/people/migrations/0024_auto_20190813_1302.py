# Generated by Django 2.2.4 on 2019-08-13 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0023_merge_20190802_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='card_description',
            field=models.TextField(blank=True, default='', max_length=400, verbose_name='Description'),
        ),
    ]
