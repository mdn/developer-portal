from unittest import mock

from django.db.models import Q
from django.test import RequestFactory, TestCase

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...home.models import HomePage
from ..models import Article, Articles


class ArticleTests(PatchedWagtailPageTests):
    """Tests for the Article page model."""

    fixtures = ["common.json"]

    def test_article_page(self):
        """Get the first article."""
        article_page = Article.objects.all().order_by("pk")[0]
        self.assertEqual(
            "Faster smarter JavaScript debugging in Firefox DevTools",
            article_page.title,
        )

    def test_article_page_topics(self):
        """Get the first article’s ‘JavaScript’ and ‘CSS’ topics."""
        article_topic_pages = Article.objects.all()[0].topics.all()
        self.assertEqual("JavaScript", article_topic_pages[0].topic.title)
        self.assertEqual("CSS", article_topic_pages[1].topic.title)

    def test_article_page_parent_pages(self):
        """An article page should only exist under the articles page."""
        self.assertAllowedParentPageTypes(Article, {Articles})

    def test_article_page_subpages(self):
        """An article page should not have child pages."""
        self.assertAllowedSubpageTypes(Article, {})

    def test_primary_topic(self):
        """An article page should have a primary topic."""
        article_page = Article.objects.all()[0]
        self.assertEqual("JavaScript", article_page.primary_topic.title)

    def read_time(self):
        """An article page should have an associated read time."""
        article_page = Article.objects.all()[0]
        self.assertEqual("1 min read", article_page.primary_topic.read_time)


class ArticlesTests(PatchedWagtailPageTests):
    """Tests for the Articles page model."""

    fixtures = ["common.json"]

    def test_articles_page(self):
        """Get the default ‘Articles’ page - WHICH IS LABELLED AS "Posts" """
        articles_page = Articles.objects.all()[0]
        self.assertEqual("Posts", articles_page.title)

    def test_articles_page_parent_pages(self):
        """The Articles page can exist under another page."""
        self.assertAllowedParentPageTypes(Articles, {HomePage})

    def test_articles_page_subpages(self):
        """The Articles page should only have article child pages."""
        self.assertAllowedSubpageTypes(Articles, {Article})


class ArticlesSearchTests(TestCase):
    "Tests for the search behaviour used by Articles().get_resources()"

    fixtures = ["common.json"]

    @classmethod
    def setUpTestData(cls):
        # Note: relies on migrations to have populated the test DB
        cls.page = Articles.objects.first()

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__calls_correct_params__no_params(
        self, mock_get_combined_articles_and_videos
    ):
        request = RequestFactory().get("/posts/")
        self.page.get_resources(request)
        mock_get_combined_articles_and_videos.assert_called_once_with(
            self.page, q_object=Q(), search_terms=None
        )

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__calls_correct_params__search_terms_only(
        self, mock_get_combined_articles_and_videos
    ):
        request = RequestFactory().get("/posts/?search=test%20test%20%3Ctest%3E")
        self.page.get_resources(request)
        mock_get_combined_articles_and_videos.assert_called_once_with(
            self.page, q_object=Q(), search_terms="test test <test>"
        )

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__search_terms_and_filters(
        self, mock_get_combined_articles_and_videos
    ):
        request = RequestFactory().get(
            "/posts/?topic=foo&topic=bar&search=testing%20test%20%3Ctesting%3E"
        )
        self.page.get_resources(request)
        mock_get_combined_articles_and_videos.assert_called_once_with(
            self.page,
            q_object=Q(topics__topic__slug__in=["foo", "bar"]),
            search_terms="testing test <testing>",
        )

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__no_search_terms_and_filters(
        self, mock_get_combined_articles_and_videos
    ):
        request = RequestFactory().get("/posts/?topic=foo&topic=bar")
        self.page.get_resources(request)
        mock_get_combined_articles_and_videos.assert_called_once_with(
            self.page,
            q_object=Q(topics__topic__slug__in=["foo", "bar"]),
            search_terms=None,
        )
