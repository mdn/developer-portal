from wagtail.tests.utils import WagtailPageTests

from ..models import Article, Articles
from ...home.models import HomePage


class ArticlesFixturesMixin():
    fixtures = [
        'common.json',
    ]


class ArticleTests(ArticlesFixturesMixin, WagtailPageTests):
    """Tests for the Article page model."""

    def test_article_page(self):
        """Get the first article."""
        article_page = Article.objects.all().order_by('pk')[0]
        self.assertEqual('Faster smarter JavaScript debugging in Firefox DevTools', article_page.title)

    def test_article_page_topics(self):
        """Get the first article’s ‘JavaScript’ and ‘CSS’ topics."""
        article_topic_pages = Article.objects.all()[0].topics.all()
        self.assertEqual('JavaScript', article_topic_pages[0].topic.title)
        self.assertEqual('CSS',        article_topic_pages[1].topic.title)

    def test_article_page_parent_pages(self):
        """An article page should only exist under the articles page."""
        self.assertAllowedParentPageTypes(Article, {Articles})

    def test_article_page_subpages(self):
        """An article page should not have child pages."""
        self.assertAllowedSubpageTypes(Article, {})

    def test_primary_topic(self):
        """An article page should have a primary topic."""
        article_page = Article.objects.all()[0]
        self.assertEqual('JavaScript', article_page.primary_topic.title)

    def read_time(self):
        """An article page should have an associated read time."""
        article_page = Article.objects.all()[0]
        self.assertEqual('1 min read', article_page.primary_topic.read_time)

    def test_article_page_related_articles(self):
        """An article page should have related article pages."""
        article_page = Article.objects.all()[0]
        related_article_pages = article_page.related_articles
        self.assertEqual(21, len(related_article_pages))


class ArticlesTests(ArticlesFixturesMixin, WagtailPageTests):
    """Tests for the Articles page model."""

    def test_articles_page(self):
        """Get the default ‘Articles’ page."""
        articles_page = Articles.objects.all()[0]
        self.assertEqual('Articles', articles_page.title)

    def test_articles_page_parent_pages(self):
        """The Articles page can exist under another page."""
        self.assertAllowedParentPageTypes(Articles, {HomePage})

    def test_articles_page_subpages(self):
        """The Articles page should only have article child pages."""
        self.assertAllowedSubpageTypes(Articles, {Article})
