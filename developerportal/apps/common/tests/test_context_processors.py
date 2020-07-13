from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings

from developerportal import context_processors

from ...content.models import ContentPage
from ...topics.models import Topics


class ContextProcessorsTestCase(TestCase):

    fixtures = ["common.json"]

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_topics_title(self):

        self.assertEqual(Topics.objects.get().title, "Products & Technologies")
        self.assertIsNone(cache.get(Topics.CACHE_KEY_TOPICS_TITLE))
        self.assertEqual(
            context_processors.topics_title(request=mock.Mock()),
            {"TOPICS_TITLE_LABEL": "Products & Technologies"},
        )
        self.assertEqual(
            cache.get(Topics.CACHE_KEY_TOPICS_TITLE), "Products & Technologies"
        )

    def test_topics_title__fallback(self):
        Topics.objects.all().delete()
        self.assertIsNone(cache.get(Topics.CACHE_KEY_TOPICS_TITLE))
        self.assertEqual(
            context_processors.topics_title(request=mock.Mock()),
            {"TOPICS_TITLE_LABEL": "Topics"},
        )
        self.assertIsNone(cache.get(Topics.CACHE_KEY_TOPICS_TITLE))

    @override_settings(BLOG_URL="https://example.com/test/")
    def test_blog_link(self):

        self.assertEqual(
            context_processors.blog_link(request=mock.Mock()),
            {"BLOG_LINK": "https://example.com/test/"},
        )

    def test_about_link(self):

        SLUG = "about"
        page = ContentPage.objects.create(
            title="TEST TITLE", path="000100010001", depth=6, slug=SLUG
        )

        self.assertEqual(
            context_processors.about_link(request=mock.Mock()),
            {"ABOUT_LINK": f"/{SLUG}/"},
        )

        # Now confirm behavior if the link is not there
        page.delete()
        self.assertEqual(
            context_processors.about_link(request=mock.Mock()), {"ABOUT_LINK": None}
        )
