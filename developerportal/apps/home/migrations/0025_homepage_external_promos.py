# Generated by Django 2.2.3 on 2019-07-26 10:33

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_auto_20190718_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='external_promos',
            field=wagtail.core.fields.StreamField([('external_promo', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock())]))], blank=True, null=True),
        ),
    ]
