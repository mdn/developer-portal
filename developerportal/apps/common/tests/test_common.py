from django.test import TestCase

from wagtail.core.models import Page

from ..utils import (
    get_combined_articles,
    get_combined_articles_and_videos,
    get_combined_events,
    get_combined_videos,
)


class UtilsTestCase(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpTestData(cls):
        cls.page = Page.objects.first()

    def test_get_combined_articles(self):
        """Getting combined articles should return items."""
        items = get_combined_articles(self.page)
        self.assertGreater(len(items), 0)

    def test_get_combined_articles_and_videos(self):
        """Getting combined articles and videos should return items."""
        items = get_combined_articles_and_videos(self.page)
        self.assertGreater(len(items), 0)

    def test_get_combined_events(self):
        """Getting combined events should not return items."""
        items = get_combined_events(self.page)
        self.assertEqual(len(items), 0)

    def test_get_combined_videos(self):
        """Getting combined articles should not return items."""
        items = get_combined_videos(self.page)
        self.assertEqual(len(items), 0)
