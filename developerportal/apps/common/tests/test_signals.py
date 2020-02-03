from unittest import mock

from django.test import TestCase

from waffle.models import Flag

from ...home.models import HomePage
from ..constants import WAFFLE_FLAG_TASK_COMPLETION


class CDNInvalidationOnWaffleFlagSaveTests(TestCase):
    def setUp(self):
        self.whitelisted_flag = Flag.objects.get(name=WAFFLE_FLAG_TASK_COMPLETION)
        self.non_whitelisted_flag = Flag(name="test_flag")
        self.non_whitelisted_flag.save()
        self.homepage = HomePage.objects.get()

    @mock.patch("developerportal.apps.common.wagtail_hooks.invalidate_entire_cdn.delay")
    def test_purge_cdn_when_whitelisted_waffle_flags_saved(
        self, mock_invalidate_entire_cdn_delay
    ):
        assert not mock_invalidate_entire_cdn_delay.called
        self.whitelisted_flag.save()
        assert mock_invalidate_entire_cdn_delay.call_count == 1

    @mock.patch("developerportal.apps.common.wagtail_hooks.invalidate_entire_cdn.delay")
    def test_purge_cdn_not_called_when_non_whitelisted_waffle_flags_saved(
        self, mock_invalidate_entire_cdn_delay
    ):
        assert not mock_invalidate_entire_cdn_delay.called
        self.non_whitelisted_flag.save()
        assert not mock_invalidate_entire_cdn_delay.called
        self.homepage.save()
        assert not mock_invalidate_entire_cdn_delay.called
