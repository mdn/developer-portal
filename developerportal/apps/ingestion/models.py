from django.db import models


class IngestionConfiguration(models.Model):

    CONTENT_TYPE_ARTICLE = "ExternalArticle"
    CONTENT_TYPE_VIDEO = "Video"

    TARGET_CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE_ARTICLE, "External Article/Blog post"),
        (CONTENT_TYPE_VIDEO, "Video post, to be embededed in portal"),
    )

    DEFAULT_DAYS_AGO_FOR_INITIAL_SYNC = 1

    source_name = models.CharField(max_length=128, help_text="A handy label")
    integration_type = models.CharField(
        choices=TARGET_CONTENT_TYPE_CHOICES, max_length=24
    )
    source_url = models.URLField(
        help_text=(
            "The URL to an appropriate data feed. "
            "We'll automatically work out the feed type"
        )
    )
    last_sync = models.DateTimeField(
        help_text=(
            "The next sync will only add items with "
            "timestamps matching or after this value."
        )
    )

    def __repr__(self):
        return "<IngestionConfiguration: {} (Synced to: {})>".format(
            self.source_name, self.last_sync.isoformat()
        )

    def __str__(self):
        return "IngestionConfiguration for {}".format(self.source_name)
