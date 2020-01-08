import datetime
from unittest import mock

from django.test import TestCase

import pytz

from ..utils import get_past_event_cutoff, paginate_resources


class EventCutoffTestCase(TestCase):
    @mock.patch("developerportal.apps.common.utils.tz_now")
    def test_get_past_event_cutoff(self, mock_tz_now):

        mock_tz_now.return_value = datetime.datetime(
            2002, 3, 5, 12, 34, 56, tzinfo=pytz.UTC
        )

        self.assertEqual(get_past_event_cutoff(), datetime.date(2002, 3, 4))


class HelperFunctionTests(TestCase):
    def test_paginate_resources__multiple_pages(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=2)
        self.assertEqual(repr(resources), "<Page 2 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(11, 21)])

    def test_paginate_resources__out_of_range(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=2342343243)
        self.assertEqual(repr(resources), "<Page 3 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(21, 26)])

    def test_paginate_resources__default(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=None)
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])

    def test_paginate_resources__not_an_integer(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref="test")
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])

    def test_paginate_resources__empty_string(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref="")
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])
