from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import Article, Articles


class ArticlesFixturesMixin():
    fixtures = [
        'topics.json',
        'articles.json',
    ]


class ArticleTests(ArticlesFixturesMixin, WagtailPageTests):
    """Tests for the Article page model."""

    def test_article_page(self):
        """Get the ‘First Post’ article."""
        article_page = Article.objects.all()[0]
        self.assertEqual('First Post', article_page.title)

    def test_article_page_topics(self):
        """Get the ‘First Post’ article’s ‘JavaScript’ and ‘CSS’ topics."""
        article_topic_pages = Article.objects.all()[0].topics.get_object_list()
        self.assertEqual('JavaScript', article_topic_pages[0].topic.title)
        self.assertEqual('CSS',        article_topic_pages[1].topic.title)

    def test_article_page_parent_pages(self):
        """An article page should only exist under the articles page."""
        self.assertAllowedParentPageTypes(Article, {Articles})

    def test_article_page_subpages(self):
        """An article page should not have child pages."""
        self.assertAllowedSubpageTypes(Article, {})

    def test_article_page_related_articles(self):
        """An article page should have related article pages."""
        article_page = Article.objects.all()[0]
        related_article_pages = article_page.get_related()
        self.assertCountEqual([], related_article_pages)


class ArticlesTests(ArticlesFixturesMixin, WagtailPageTests):
    """Tests for the Articles page model."""

    def test_articles_page(self):
        """Get the default ‘Articles’ page."""
        articles_page = Articles.objects.all()[0]
        self.assertEqual('Articles', articles_page.title)

    def test_articles_page_parent_pages(self):
        """The Articles page can exist under another page."""
        self.assertAllowedParentPageTypes(Articles, {Page})

    def test_articles_page_subpages(self):
        """The Articles page should only have child pages of type article."""
        self.assertAllowedSubpageTypes(Articles, {Article})
