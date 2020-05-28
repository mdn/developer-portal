import datetime
from unittest import mock

from django.test import TestCase

import pytz
from wagtail.admin.edit_handlers import get_form_for_model
from wagtail.core.models import Page, Site

from ..forms import BasePageForm
from ..utils import (
    get_combined_articles,
    get_combined_articles_and_videos,
    get_combined_events,
    get_combined_videos,
    get_past_event_cutoff,
    paginate_resources,
)


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


class HelperFunctionTestsWithFixtures(TestCase):
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
                "for a post: https://example.com/posts/your-slug-here/"
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
                "for a post: http://localhost/posts/your-slug-here/"
            ),
        )

    def test_help_text_patching_for_external_content(self):
        # Inline import because we need to use a subclass of Page and don't
        # want to pollute this module more than we have to
        from developerportal.apps.externalcontent.models import (
            ExternalEvent,
            ExternalContent,
            ExternalVideo,
            ExternalArticle,
        )

        for model in [ExternalEvent, ExternalContent, ExternalVideo, ExternalArticle]:
            assert model.base_form_class == BasePageForm

            FormClass = get_form_for_model(model, form_class=BasePageForm)
            form = FormClass()

            self.assertEqual(
                form.fields["slug"].help_text,
                (
                    "Because you are adding External content, "
                    "this slug will NOT be visible to the end user, "
                    "but still needs to be unique within the CMS."
                ),
            )
