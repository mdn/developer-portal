from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import Article, Articles


class ArticleTests(WagtailPageTests):
    """Tests for the Article page model."""

    def test_article_parent_pages(self):
        self.assertAllowedParentPageTypes(Article, {Articles})

    def test_article_subpages(self):
        self.assertAllowedSubpageTypes(Article, {})


class ArticlesTests(WagtailPageTests):
    """Tests for the Articles page model."""

    def test_articles_parent_pages(self):
        self.assertAllowedParentPageTypes(Articles, {Page})

    def test_articles_subpages(self):
        self.assertAllowedSubpageTypes(Articles, {Article})
