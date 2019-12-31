import datetime
from unittest import mock

from django.test import TestCase

import pytz

from ..utils import get_all_urls_from_sitemap, get_past_event_cutoff, paginate_resources


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


class HelperFunctionTestsRequiringFixtures(TestCase):

    fixtures = ["common.json"]

    def test_get_all_urls_from_sitemap(self):

        urls = get_all_urls_from_sitemap()
        self.assertEqual(len(urls), 32)

        hostname = "http://developer-portal-127-0-0-1.nip.io:433"  # from common.json

        expected = [
            f"{hostname}/",
            f"{hostname}/topics/",
            f"{hostname}/topics/css/",
            f"{hostname}/topics/javascript/",
            f"{hostname}/posts/",
            f"{hostname}/posts/faster-smarter-javascript-debugging-in-firefox/",
            (
                f"{hostname}/posts/"
                "developer-roadshow-2019-returns-vr-iot-and-all-things-web/"
            ),
            (
                f"{hostname}/posts/"
                "standardizing-wasi-system-interface-run-webassembly-outside-web/"
            ),
            f"{hostname}/posts/firefox-66-sound-silence/",
            f"{hostname}/posts/fearless-security-thread-safety/",
            f"{hostname}/posts/how-make-vr-web-new-video-series/",
            f"{hostname}/posts/firefox-67-dark-mode-css-webrender-and-more/",
            f"{hostname}/posts/web-design-survey-findings-and-next-steps/",
            f"{hostname}/posts/9-biggest-mistakes-css-grid/",
            f"{hostname}/posts/technical-details-recent-firefox-add-outage/",
            f"{hostname}/posts/scroll-anchoring-firefox-66/",
            f"{hostname}/posts/javascript-and-evidence-based-language-design/",
            (
                f"{hostname}/posts/"
                "calls-between-javascript-and-webassembly-are-finally-fast/"
            ),
            f"{hostname}/posts/es6-depth-iterators-and-loop/",
            f"{hostname}/posts/es6-depth-destructuring/",
            f"{hostname}/posts/indicating-focus-improve-accessibility/",
            (
                f"{hostname}/posts/"
                "fluent-10-localization-system-natural-sounding-translations/"
            ),
            f"{hostname}/posts/overscripted-digging-javascript-execution-scale/",
            (
                f"{hostname}/posts/firefox-brings-you-smooth-"
                "video-playback-with-the-worlds-fastest-av1-decoder/"
            ),
            f"{hostname}/posts/depths-technical-details-behind-av1/",
            f"{hostname}/posts/new-firefox-devtools-65/",
            f"{hostname}/posts/css-grid-level-2-subgrid-is-coming-to-firefox/",
            f"{hostname}/events/",
            f"{hostname}/communities/",
            f"{hostname}/communities/people/",
            f"{hostname}/communities/people/josh-marinacci/",
            f"{hostname}/videos/",
        ]

        self.assertEqual(urls, expected)
