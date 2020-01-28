# Generated by Django 2.2.9 on 2020-01-28 15:45
import logging
from django.db import migrations

logger = logging.getLogger(__name__)

FLAG_PARAMS = {
    "name": "show_task_completion_survey",
    "everyone": None,
    "percent": "5",
    "testing": False,
    "superusers": False,
    "staff": False,
    "authenticated": False,
    "note": "Required for the User Task Completion survey to be selectively shown",
}


def forwards(apps, schema_editor):
    Flag = apps.get_model("waffle", "Flag")
    if Flag.objects.filter(name=FLAG_PARAMS["name"]).count() == 0:
        logger.info(f"Creating new django-waffle flag using {FLAG_PARAMS}")
        flag = Flag(**FLAG_PARAMS)
        flag.save()
    else:
        logger.info(f"A django-waffle Flag for {FLAG_PARAMS['name']} already exists")


def backwards(apps, schema_editor):
    Flag = apps.get_model("waffle", "Flag")
    logger.info(f"Deleting any django-waffle Flag called {FLAG_PARAMS['name']}")
    deleted = Flag.objects.filter(name=FLAG_PARAMS["name"]).delete()
    logger.info(f"Deleted records: {deleted}")


class Migration(migrations.Migration):
    """Add a django-waffle Flag which we need for the user task-completion survey"""

    dependencies = [
        ("waffle", "0003_update_strings_for_i18n"),
        ("common", "0002_drop_staticbuild_tables"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
