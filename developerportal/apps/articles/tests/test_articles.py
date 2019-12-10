from unittest import mock

from django.test import RequestFactory

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

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__pagination_multiple_pages(self, mock_get):
        mock_get.return_value = [x for x in range(1, 26)]  # [1... 25]
        factory = RequestFactory()
        request = factory.get("/?page=2")
        articles_page = Articles.objects.all()[0]
        resources = articles_page.get_resources(request)
        self.assertEqual(repr(resources), "<Page 2 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(11, 21)])

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__pagination_out_of_range(self, mock_get):
        mock_get.return_value = [x for x in range(1, 26)]  # [1... 25]
        factory = RequestFactory()
        request = factory.get("/?page=2342423")
        articles_page = Articles.objects.all()[0]
        resources = articles_page.get_resources(request)
        self.assertEqual(repr(resources), "<Page 3 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(21, 26)])

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__pagination_default(self, mock_get):
        mock_get.return_value = [x for x in range(1, 26)]  # [1... 25]
        factory = RequestFactory()
        request = factory.get("/")
        articles_page = Articles.objects.all()[0]
        resources = articles_page.get_resources(request)
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])

    @mock.patch("developerportal.apps.articles.models.get_combined_articles_and_videos")
    def test_get_resources__pagination_not_an_integer(self, mock_get):
        mock_get.return_value = [x for x in range(1, 26)]  # [1... 25]
        factory = RequestFactory()
        request = factory.get("/page=?test")
        articles_page = Articles.objects.all()[0]
        resources = articles_page.get_resources(request)
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])


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
