# Generated by Django 2.2.1 on 2019-07-02 13:18

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0022_auto_20190702_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='get_started',
            field=wagtail.core.fields.StreamField([('panel', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.TextBlock()), ('button_text', wagtail.core.blocks.CharBlock()), ('page_link', wagtail.core.blocks.PageChooserBlock(required=False)), ('external_link', wagtail.core.blocks.URLBlock(required=False))]))]),
        ),
    ]
