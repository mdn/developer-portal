# Generated by Django 2.2.4 on 2019-08-13 14:35

import datetime
import developerportal.apps.common.fields
from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0028_merge_20190805_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=wagtail.core.fields.StreamField([('author', wagtail.core.blocks.PageChooserBlock(page_type=['people.Person'])), ('external_author', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Name')), ('image', wagtail.images.blocks.ImageChooserBlock()), ('url', wagtail.core.blocks.URLBlock(label='URL', required=False))]))], blank=True, help_text='Optional list of the article’s authors. Use ‘External author’ to add guest authors without creating a profile on the system', null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=developerportal.apps.common.fields.CustomStreamField([('paragraph', wagtail.core.blocks.RichTextBlock(features=('h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'blockquote', 'code', 'hr'))), ('image', wagtail.images.blocks.ImageChooserBlock()), ('button', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.CharBlock()), ('page_link', wagtail.core.blocks.PageChooserBlock(required=False)), ('external_link', wagtail.core.blocks.URLBlock(help_text='External URL to link to instead of a page.', required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('embed_html', wagtail.core.blocks.RawHTMLBlock(help_text='Warning: be careful what you paste here, since this field could introduce XSS (or similar) bugs. This field is meant solely for third-party embeds.')), ('code_snippet', wagtail.core.blocks.StructBlock([('language', wagtail.core.blocks.ChoiceBlock(choices=[('css', 'CSS'), ('go', 'Go'), ('html', 'HTML'), ('js', 'JavaScript'), ('python', 'Python'), ('rust', 'Rust'), ('ts', 'TypeScript')])), ('code', wagtail.core.blocks.TextBlock())]))], default=None, help_text='The main article content. Supports rich text, images, embed via URL, embed via HTML, and inline code snippets'),
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateField(default=datetime.date.today, help_text='The date the article was published', verbose_name='Article date'),
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Optional short text description, max. 250 characters', max_length=250),
        ),
        migrations.AlterField(
            model_name='article',
            name='related_links_mdn',
            field=wagtail.core.fields.StreamField([('link', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Name')), ('url', wagtail.core.blocks.URLBlock())]))], blank=True, help_text='Optional links to MDN Web Docs for further reading', null=True, verbose_name='Related MDN links'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Optional short text description, max. 250 characters', max_length=250),
        ),
    ]
