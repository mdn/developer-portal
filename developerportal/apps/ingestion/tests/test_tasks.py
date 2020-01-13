from unittest import mock

from django.test import TestCase, override_settings

from ..models import IngestionConfiguration
from ..tasks import ingest_articles, ingest_videos


@override_settings(AUTOMATICALLY_INGEST_CONTENT=True)
class TaskTests(TestCase):
    @mock.patch("developerportal.apps.ingestion.tasks.ingest_content")
    def test_ingest_articles(self, mock_ingest_content):
        ingest_articles()
        mock_ingest_content.assert_called_once_with(
            type_=IngestionConfiguration.CONTENT_TYPE_ARTICLE
        )

    @mock.patch("developerportal.apps.ingestion.tasks.ingest_content")
    def test_ingest_videos(self, mock_ingest_content):
        ingest_videos()
        mock_ingest_content.assert_called_once_with(
            type_=IngestionConfiguration.CONTENT_TYPE_VIDEO
        )

    @override_settings(AUTOMATICALLY_INGEST_CONTENT=False)
    @mock.patch("developerportal.apps.ingestion.tasks.ingest_content")
    def test_ingest_articles__disabled_via_settings(self, mock_ingest_content):
        ingest_articles()
        assert not mock_ingest_content.called

    @override_settings(AUTOMATICALLY_INGEST_CONTENT=False)
    @mock.patch("developerportal.apps.ingestion.tasks.ingest_content")
    def test_ingest_videos__disabled_via_settings(self, mock_ingest_content):
        ingest_videos()
        assert not mock_ingest_content.called
