from unittest import mock

from django.test import TestCase

from wagtail.core.models import Page
from wagtail.core.signals import page_published, page_unpublished


class SignalsTestCase(TestCase):
    @mock.patch(
        "developerportal.apps.taskqueue.wagtail_hooks.invalidate_entire_cdn.delay"
    )
    def test_cdn_invalidation_signal_handler(self, mock_invalidate_entire_cdn__delay):

        cases = [{"signal": page_published}, {"signal": page_unpublished}]

        for case in cases:
            mock_invalidate_entire_cdn__delay.reset_mock()
            with self.subTest(case=case):
                case["signal"].send(sender=Page, instance=None)
                mock_invalidate_entire_cdn__delay.assert_called_once_with()
