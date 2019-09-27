from django.test import TestCase

from wagtail.admin.edit_handlers import get_form_for_model
from wagtail.core.models import Page, Site

from ..forms import BasePageForm
from ..utils import (
    get_combined_articles,
    get_combined_articles_and_videos,
    get_combined_events,
    get_combined_videos,
)


class UtilsTestCase(TestCase):
    fixtures = ["common.json"]

    @classmethod
    def setUpTestData(cls):
        # Note: relies on migrations to have populated the test DB
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


class BasePageFormTestCase(TestCase):
    @classmethod
    def setUp(cls):
        # Inline import because we need to use a subclass of Page and don't
        # want to pollute this module more than we have to
        from developerportal.apps.articles.models import Article

        cls.Article = Article

    def test_help_text_patching__no_site(self):
        # Note: relies on migrations to have populated the test DB
        Site.objects.all().delete()
        assert not Site.objects.exists()

        assert self.Article.base_form_class == BasePageForm
        FormClass = get_form_for_model(self.Article, form_class=BasePageForm)
        form = FormClass()

        self.assertEqual(
            form.fields["slug"].help_text,
            (
                "The name of the page as it will appear in URLs. For example, "
                "for an Article: https://example.com/articles/slug/"
            ),
        )

    def test_help_text_patching__has_site(self):
        # Note: relies on migrations to have populated the test DB
        assert Site.objects.exists()
        assert Site.objects.first().hostname == "localhost"

        assert self.Article.base_form_class == BasePageForm
        FormClass = get_form_for_model(self.Article, form_class=BasePageForm)
        form = FormClass()

        self.assertEqual(
            form.fields["slug"].help_text,
            (
                "The name of the page as it will appear in URLs. For example, "
                "for an Article: http://localhost/articles/slug/"
            ),
        )
