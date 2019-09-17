# Generated by Django 2.2.3 on 2019-07-08 08:58

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [("events", "0002_auto_20190704_1334")]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="speakers",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "speaker",
                        wagtail.core.blocks.PageChooserBlock(
                            page_type=["people.Person"], required=False
                        ),
                    ),
                    (
                        "external_speaker",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("title", wagtail.core.blocks.CharBlock(label="Name")),
                                ("job_title", wagtail.core.blocks.CharBlock()),
                                (
                                    "profile_picture",
                                    wagtail.images.blocks.ImageChooserBlock(),
                                ),
                            ],
                            required=False,
                        ),
                    ),
                ],
                blank=True,
                null=True,
            ),
        )
    ]
