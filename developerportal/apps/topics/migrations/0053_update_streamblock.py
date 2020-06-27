# Generated by Django 2.2.12 on 2020-05-12 15:54

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0052_auto_20200511_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='featured',
            field=wagtail.core.fields.StreamField([('post', wagtail.core.blocks.PageChooserBlock(page_type=['articles.Article', 'externalcontent.ExternalArticle'])), ('external_page', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='16:9 aspect-ratio image', label='16:9 image')), ('image_3_2', wagtail.images.blocks.ImageChooserBlock(help_text='3:2 aspect-ratio image - optiopnal but recommended', label='3:2 image', required=False))]))], blank=True, help_text='Optional space for featured items, max. 7', null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='recent_work',
            field=wagtail.core.fields.StreamField([('post', wagtail.core.blocks.PageChooserBlock(page_type=['articles.Article', 'externalcontent.ExternalArticle'])), ('external_page', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='16:9 aspect-ratio image', label='16:9 image')), ('image_3_2', wagtail.images.blocks.ImageChooserBlock(help_text='3:2 aspect-ratio image - optiopnal but recommended', label='3:2 image', required=False))])), ('video', wagtail.core.blocks.PageChooserBlock(page_type=['videos.Video', 'externalcontent.ExternalVideo']))], blank=True, help_text='Optional space for featured posts, videos or links, min. 1, max. 4.', null=True),
        ),
    ]
