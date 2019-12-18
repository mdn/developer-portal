import datetime
from unittest import mock

from django.test import TestCase

import pytz

from ..utils import get_past_event_cutoff


class EventCutoffTestCase(TestCase):
    @mock.patch("developerportal.apps.common.utils.tz_now")
    def test_get_past_event_cutoff(self, mock_tz_now):

        mock_tz_now.return_value = datetime.datetime(
            2002, 3, 5, 12, 34, 56, tzinfo=pytz.UTC
        )

        self.assertEqual(get_past_event_cutoff(), datetime.date(2002, 3, 4))
