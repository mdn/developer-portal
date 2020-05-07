# Generated by Django 2.2.12 on 2020-05-07 12:15

"""Copy any image set as `Event.image` to populate the `Event.card_image` field
instead, including updating the latest revision of the page (draft or live)"""

from django.db import migrations

from developerportal.apps.common.migration_utils import (
    move_Page_image_to_Page_card_image,
)


def forwards(apps, schema_editor):
    PageSubclass = apps.get_model("events", "Event")
    move_Page_image_to_Page_card_image(PageSubclass)


class Migration(migrations.Migration):

    dependencies = [("events", "0021_auto_20200326_1339")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
