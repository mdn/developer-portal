# Generated by Django 2.2.3 on 2019-07-08 11:00

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20190708_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='speakers',
            field=wagtail.core.fields.StreamField([('speaker', wagtail.core.blocks.PageChooserBlock(page_type=['people.Person'], required=False)), ('external_speaker', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Name')), ('job_title', wagtail.core.blocks.CharBlock()), ('profile_picture', wagtail.images.blocks.ImageChooserBlock()), ('url', wagtail.core.blocks.URLBlock(label='URL', required=False))], required=False))], blank=True, null=True),
        ),
    ]
