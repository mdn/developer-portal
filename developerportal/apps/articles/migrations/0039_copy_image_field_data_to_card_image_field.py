# Generated by Django 2.2.12 on 2020-05-06 22:10

"""Copy any image set as `Article.image` to populate the `Article.card_image` field
instead, including updating the latest revision of the page (draft or live)"""

from django.db import migrations

from developerportal.apps.common.migration_utils import (
    move_Page_image_to_Page_card_image,
)


def forwards(apps, schema_editor):
    PageSubclass = apps.get_model("articles", "Article")
    move_Page_image_to_Page_card_image(PageSubclass)


class Migration(migrations.Migration):

    dependencies = [("articles", "0038_rename_related_links_without_data_port")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
