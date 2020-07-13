# Generated by Django 2.2.9 on 2020-01-15 17:19
"""
Drop tables from the `staticbuild` app, if they still exist,
following the removal of it from the codebase.
"""

import logging

from django.db import connection
from django.db import migrations

logger = logging.getLogger(__name__)


def drop_staticbuild_table(apps, schema_editor):
    # We're not expecting any cascade. Here's the schema:
    #  Table "public.staticbuild_staticbuild"
    #  Column |           Type           | Collation | Nullable |                       Default  # noqa
    # --------+--------------------------+-----------+----------+-----------------------------------------------------
    #  id     | integer                  |           | not null | nextval('staticbuild_staticbuild_id_seq'::regclass)  # noqa
    #  date   | timestamp with time zone |           | not null |
    # Indexes:
    #     "staticbuild_staticbuild_pkey" PRIMARY KEY, btree (id)

    table_name = "staticbuild_staticbuild"
    logger.info("Dropping redundant DB table %s", table_name)
    with connection.cursor() as cursor:
        query = f"DROP TABLE IF EXISTS {table_name}"
        logger.info(f"Query: {query}")
        cursor.execute(query)


class Migration(migrations.Migration):

    dependencies = [("common", "0001_drop_social_auth_app_tables")]

    operations = [
        # DISABLED BECAUSE WE NO LONGER NEED IT, BUT KEPT FOR REFERENCE
        # migrations.RunPython(drop_staticbuild_table, migrations.RunPython.noop)
    ]
