# Generated by Django 2.2.4 on 2019-08-13 15:03

import datetime
from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [("externalcontent", "0019_auto_20190813_1302")]

    operations = [
        migrations.AlterField(
            model_name="externalarticle",
            name="authors",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "author",
                        wagtail.core.blocks.PageChooserBlock(
                            page_type=["people.Person"]
                        ),
                    ),
                    (
                        "external_author",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("title", wagtail.core.blocks.CharBlock(label="Name")),
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "url",
                                    wagtail.core.blocks.URLBlock(
                                        label="URL", required=False
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
                help_text="Optional list of the article’s authors. Use ‘External author’ to add guest authors without creating a profile on the system",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="externalarticle",
            name="date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="The date the article was published",
                verbose_name="Article date",
            ),
        ),
        migrations.AlterField(
            model_name="externalcontent",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Optional short text description, max. 400 characters",
                max_length=400,
            ),
        ),
        migrations.AlterField(
            model_name="externalcontent",
            name="external_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="The URL that this content links to, max. 2048 characters for compatibility with older web browsers",
                max_length=2048,
                verbose_name="URL",
            ),
        ),
        migrations.AlterField(
            model_name="externalevent",
            name="end_date",
            field=models.DateField(
                blank=True,
                help_text="The date the event is scheduled to end",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="externalevent",
            name="start_date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="The date the event is scheduled to start",
            ),
        ),
        migrations.AlterField(
            model_name="externalvideo",
            name="date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="The date the video was published",
                verbose_name="Video date",
            ),
        ),
        migrations.AlterField(
            model_name="externalvideo",
            name="duration",
            field=models.CharField(
                blank=True,
                help_text="Optional video duration in MM:SS format e.g. “12:34”. Shown when the video is displayed as a card",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="externalvideo",
            name="speakers",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "speaker",
                        wagtail.core.blocks.PageChooserBlock(
                            page_type=["people.Person"], required=False
                        ),
                    )
                ],
                blank=True,
                help_text="Optional list of people associated with or starring in the video",
                null=True,
            ),
        ),
    ]
