# Generated by Django 2.2.1 on 2019-06-27 15:23

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20190625_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='featured',
            field=wagtail.core.fields.StreamField([], blank=True, null=True),
        ),
    ]
