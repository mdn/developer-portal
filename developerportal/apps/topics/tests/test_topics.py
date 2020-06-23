from unittest import mock

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...content.models import ContentPage
from ...home.models import HomePage
from ..models import Topic, Topics, check_for_svg_file


class TopicTests(PatchedWagtailPageTests):
    """Tests for the Topic page model."""

    fixtures = ["common.json"]

    def test_topic_page(self):
        """Get the ‘CSS’ topic."""
        topic_page = Topic.objects.all()[0]
        self.assertEqual("CSS", topic_page.title)

    def test_topic_page_parent_pages(self):
        """A topic page should only exist under the topics page."""
        self.assertAllowedParentPageTypes(Topic, {Topics})

    def test_topic_page_subpages(self):
        """A topic page should not have child pages."""
        self.assertAllowedSubpageTypes(Topic, {ContentPage})

    def test_topic_page_articles(self):
        """A topic page should have article pages."""
        topic_page = Topic.objects.all()[0]
        topic_page_article = topic_page.articles[0].article
        self.assertEqual(
            "Faster smarter JavaScript debugging in Firefox DevTools",
            topic_page_article.title,
        )


class TopicsTests(PatchedWagtailPageTests):
    """Tests for the Topics page model."""

    fixtures = ["common.json"]

    def setUp(self):
        # purge any Topic titles we unintentionally cache
        cache.clear()

    def tearDown(self):
        # purge any Topic titles we unintentionally cache
        cache.clear()

    def test_topics__page_parent_pages(self):
        """The Topics page can exist under another page."""
        self.assertAllowedParentPageTypes(Topics, {HomePage})

    def test_topics_page_subpages(self):
        """The Topics page should only have topic child pages."""
        self.assertAllowedSubpageTypes(Topics, {Topic})

    def test_save_invalidates_relevant_cached_content(self):

        topic_page = Topics.published_objects.get()

        for key in topic_page._bulk_invalidation_cache_keys:
            self.assertIsNone(cache.get(key))

        for i, key in enumerate(topic_page._bulk_invalidation_cache_keys):
            cache.set(key, "test{i}")

        for key in topic_page._bulk_invalidation_cache_keys:
            self.assertIsNotNone(cache.get(key))

        topic_page.save()

        for key in topic_page._bulk_invalidation_cache_keys:
            self.assertIsNone(cache.get(key))


class SVGFileCheckTests(TestCase):
    def test_check_for_svg_file(self):
        # A light test of a naive safety-net validation rule
        mock_field = mock.Mock("mock-FileField")
        mock_file = mock.Mock(name="mock-File")
        mock_field.file = mock_file

        # Should fail:
        for filename in ["foo.jpg", "foo.png", "foo.webp"]:
            with self.subTest(filename=filename):
                type(mock_file).name = filename
                with self.assertRaises(ValidationError):
                    check_for_svg_file(mock_field)

        # Should be fine:
        type(mock_file).name = "foo.svg"
        check_for_svg_file(mock_field)
