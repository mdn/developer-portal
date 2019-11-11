# Generated by Django 2.2.6 on 2019-11-01 13:29

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0046_remove_topic_tabbed_panels_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='featured',
            field=wagtail.core.fields.StreamField([('post', wagtail.core.blocks.PageChooserBlock(page_type=['articles.Article', 'externalcontent.ExternalArticle'])), ('external_page', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock())]))], blank=True, help_text='Optional space for featured posts, max. 4', null=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='latest_articles_count',
            field=models.IntegerField(choices=[(3, '3'), (6, '6'), (9, '9')], default=3, help_text='The number of posts to display for this topic.'),
        ),
    ]
