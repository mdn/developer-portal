# Generated by Django 2.2.11 on 2020-03-23 18:09

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0050_remove_topic_latest_articles_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='tabbed_panels',
        ),
        migrations.AddField(
            model_name='topic',
            name='recent_work',
            field=wagtail.core.fields.StreamField([('post', wagtail.core.blocks.PageChooserBlock(page_type=['articles.Article', 'externalcontent.ExternalArticle'])), ('external_page', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock())])), ('video', wagtail.core.blocks.PageChooserBlock(page_type=['videos.Video', 'externalcontent.ExternalVideo']))], blank=True, help_text='Optional space for featured posts, videos or links, min. 1, max. 4.', null=True),
        ),
    ]
