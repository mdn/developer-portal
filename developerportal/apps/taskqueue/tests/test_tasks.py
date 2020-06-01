from unittest import mock

from django.test import TestCase

from ..tasks import (
    invalidate_entire_cdn,
    selectively_invalidate_cdn,
    update_wagtail_search_index,
)


class TasksTestCase(TestCase):
    fixtures = ["common.json"]

    @mock.patch("developerportal.apps.taskqueue.tasks.invalidate_cdn")
    def test_invalidate_entire_cdn(self, mock_invalidate_cdn):

        assert not mock_invalidate_cdn.called
        invalidate_entire_cdn()
        mock_invalidate_cdn.assert_called_once_with()

    @mock.patch("developerportal.apps.taskqueue.tasks.invalidate_cdn")
    def test_selectively_invalidate_cdn(self, mock_invalidate_cdn):

        assert not mock_invalidate_cdn.called
        selectively_invalidate_cdn()
        mock_invalidate_cdn.assert_called_once_with(
            invalidation_targets=["/events/*", "/communities/people/*", "/topics/*"]
        )

    @mock.patch("developerportal.apps.taskqueue.tasks.call_command")
    def test_update_wagtail_search_index(self, mock_call_command):
        assert not mock_call_command.called
        update_wagtail_search_index()
        mock_call_command.assert_called_once_with("wagtail_update_index")


class ConfigurationTestCase(TestCase):

    # Disable the autodiscovery when importing for the test
    @mock.patch("developerportal.apps.taskqueue.celery.app.autodiscover_tasks")
    def test_expected_tasks_are_configured(self, mock_autodiscover_tasks):
        # Light check that things are still plugged in...
        from ..celery import app

        configured_tasks = [x["task"] for x in app.conf.beat_schedule.values()]

        self.assertEqual(
            sorted(
                [
                    "developerportal.apps.taskqueue.tasks.publish_scheduled_pages",
                    "developerportal.apps.taskqueue.tasks.selectively_invalidate_cdn",
                    "developerportal.apps.ingestion.tasks.ingest_articles",
                    "developerportal.apps.ingestion.tasks.ingest_videos",
                    "developerportal.apps.taskqueue.tasks.update_wagtail_search_index",
                ]
            ),
            sorted(configured_tasks),
        )
