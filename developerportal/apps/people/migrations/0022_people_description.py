# Generated by Django 2.2.3 on 2019-08-02 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0021_auto_20190731_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='description',
            field=models.TextField(blank=True, default='', max_length=250, verbose_name='Description'),
        ),
    ]
