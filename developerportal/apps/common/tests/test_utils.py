import datetime
from unittest import mock

from django.db.models import Q
from django.test import TestCase

import pytz
from wagtail.admin.edit_handlers import get_form_for_model
from wagtail.core.models import Page, Site

from ..forms import BasePageForm
from ..utils import (
    _prep_search_terms,
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

    def test_prep_search_terms(self):
        cases = (
            {"desc": "Empty input", "input": "", "expected": ""},
            {
                "desc": "Unescape urlencoded params",
                "input": "Hello%20World%21",
                "expected": "Hello World!",
            },
            {"desc": "Just spaces", "input": "     ", "expected": ""},
            {
                "desc": "Markup escaped via bleach",
                "input": "<script>alert('boo');</script>",
                "expected": "&lt;script&gt;alert('boo');&lt;/script&gt;",
            },
            {"desc": "No change 1", "input": "findme", "expected": "findme"},
            {
                "desc": "No change 2",
                "input": "Hello, World!",
                "expected": "Hello, World!",
            },
            {
                "desc": "Unicode decoding",
                "input": "Hello\u2014World!",
                "expected": "Hello—World!",
            },
            {
                "desc": "Unicode in input",
                "input": "Amélie Zoë Fougères",
                "expected": "Amélie Zoë Fougères",
            },
            {
                "desc": "Drop tabs and returns 1",
                "input": "\t\t\n\r\ntest\r\nparams",
                "expected": "testparams",  # Controversial?
            },
            {
                "desc": "Drop tabs and returns 2: retain the spaces",
                "input": "\t\t\n\r\ntest \r\nparams",
                "expected": "test params",
            },
        )

        for case in cases:
            with self.subTest(msg=case["desc"]):
                self.assertEqual(_prep_search_terms(case["input"]), case["expected"])


class HelperFunctionTestsWithFixtures(TestCase):
    fixtures = ["common_plus_extras_for_search_tests.json"]

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
        self.assertEqual(len(items), 2 + 1)

    def test_get_combined_FOOs__unpublished_pages_ignored(self):

        Page.objects.all().unpublish()
        # All of the below are tested with live/published pages, so this is the opposite

        for _callable in [
            get_combined_articles,
            get_combined_articles_and_videos,
            get_combined_events,
            get_combined_videos,
        ]:
            self.assertEqual(len(_callable(self.page)), 0)


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


class CustomSearchTests(TestCase):
    # These are similar to what we have in test_articles.py, but the focus
    # here is on the utility function

    fixtures = ["common_plus_extras_for_search_tests.json"]

    @classmethod
    def setUpTestData(cls):
        # Note: relies on migrations to have populated the test DB
        cls.page = Page.objects.first()
        # The type of page that cls.page is is irrelevant to the search results
        # we get back; it's passed to ensure it is not returned in the results,
        # so as long as it's not an Article, Video, ExternalArticle or
        # ExternalVideo it's fine:
        assert cls.page.title == "Root"

    def test_get_combined_articles_and_videos__search_terms_only(self):

        cases = [
            {
                "desc": "No params (empty string) so no narrower scoping",
                "terms": "",
                "expected_count": 22 + 2 + 1 + 2,
            },
            {
                "desc": "No params (None) so no narrower scoping",
                "terms": None,
                "expected_count": 22 + 2 + 1 + 2,
            },
            {
                "desc": "Title match",
                "terms": "subgrid is coming to Firefox",
                "expected_count": 1,
                "page_ids": [32],
            },
            {
                "desc": "Description match",
                "terms": "CSS Grid Specification",
                "expected_count": 1,
                "page_ids": [32],
            },
            {
                "desc": "Broader match",
                "terms": "DevTools",
                "expected_count": 6,
                "page_ids": [8, 18, 22, 31, 38, 39],
                # 38 is a video, 39 is an externalarticle, rest are articles
            },
            {
                "desc": "Targetted title match: Video",
                "terms": "An Update on Firefox and Mozilla, Summer 2019",
                "expected_count": 1,
                "page_ids": [37],
            },
            {
                "desc": "Targetted description match: Video",
                "terms": (
                    "better understand how the browser "
                    "interprets the CSS values we assign"
                ),
                "expected_count": 1,
                "page_ids": [38],
            },
            {
                "desc": "Targetted title match: Article",
                "terms": "all things web",
                "expected_count": 1,
                "page_ids": [12],
            },
            {
                "desc": "Targetted description match: Article",
                "terms": "fix bugs quickly and efficiently",
                "expected_count": 1,
                "page_ids": [8],
            },
            {
                "desc": "Targetted title match: ExternalVideo",
                "terms": "Firefox Font Editor",  # Note the lack of possessive
                "expected_count": 1,
                "page_ids": [41],
            },
            {
                "desc": "Targetted description match: ExternalVideo",
                "terms": "Firefox's font editor",  # Note the apostrophe
                "expected_count": 1,
                "page_ids": [41],
            },
            {
                "desc": "Targetted title match: ExternalArticle",
                "terms": "DNS over HTTPS",
                "expected_count": 1,
                "page_ids": [40],
            },
            {
                "desc": "Targetted description match: ExternalArticle",
                "terms": "secure your DNS",
                "expected_count": 1,
                "page_ids": [40],
            },
        ]
        for case in cases:
            with self.subTest(msg=case["desc"]):
                items = get_combined_articles_and_videos(
                    self.page, search_terms=case["terms"]
                )
                _expected_count = case["expected_count"]
                self.assertEqual(len(items), _expected_count, items)
                if case.get("page_ids") is not None:
                    self.assertEqual(
                        sorted([page.id for page in items]), case["page_ids"]
                    )

    def test_get_combined_articles_and_videos__no_search_terms_and_filters(self):
        q_object = Q(topics__topic__slug__in=["css", "javascript"])
        items = get_combined_articles_and_videos(self.page, q_object=q_object)
        self.assertEqual(len(items), 22)

    def test_get_combined_articles_and_videos__search_terms_and_filters(self):
        q_object = Q(topics__topic__slug__in=["css", "javascript"])
        items = get_combined_articles_and_videos(
            self.page, q_object=q_object, search_terms="Destructuring"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 25)
        self.assertEqual(items[0].title, "ES6 In Depth: Destructuring")
