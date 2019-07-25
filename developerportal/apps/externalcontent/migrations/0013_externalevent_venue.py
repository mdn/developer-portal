# Generated by Django 2.2.3 on 2019-07-24 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0012_auto_20190724_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalevent',
            name='venue',
            field=models.TextField(blank=True, default='', help_text='Full address of the event venue, displayed on the event detail page', max_length=250),
        ),
    ]
