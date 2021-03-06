# Generated by Django 2.2.9 on 2020-01-02 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IngestionConfiguration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "source_name",
                    models.CharField(help_text="A handy label", max_length=128),
                ),
                (
                    "integration_type",
                    models.CharField(
                        choices=[
                            ("ExternalArticle", "External Article/Blog post"),
                            ("Video", "Video post, to be embededed in portal"),
                        ],
                        max_length=24,
                    ),
                ),
                (
                    "source_url",
                    models.URLField(
                        help_text="The URL to an appropriate data feed. We'll automatically work out the feed type"
                    ),
                ),
                (
                    "last_sync",
                    models.DateTimeField(
                        help_text="The next sync will only add items with timestamps matching or after this value."
                    ),
                ),
            ],
        )
    ]
