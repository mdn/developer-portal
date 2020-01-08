from unittest import mock

from django.test import TestCase

from ..tasks import invalidate_entire_cdn, selectively_invalidate_cdn


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
