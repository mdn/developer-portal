from wagtail.tests.utils import WagtailPageTests

from ..models import Topic, Topics
from ...home.models import HomePage


class TopicTests(WagtailPageTests):
    """Tests for the Topic page model."""

    fixtures = ['common.json']

    def test_topic_page(self):
        """Get the ‘CSS’ topic."""
        topic_page = Topic.objects.all()[0]
        self.assertEqual('CSS', topic_page.title)

    def test_topic_page_parent_pages(self):
        """A topic page should only exist under the topics page."""
        self.assertAllowedParentPageTypes(Topic, {Topics})

    def test_topic_page_subpages(self):
        """A topic page should not have child pages."""
        self.assertAllowedSubpageTypes(Topic, {})

    def test_topic_page_articles(self):
        """A topic page should have article pages."""
        topic_page = Topic.objects.all()[0]
        topic_page_article = topic_page.articles[0].article
        self.assertEqual('Faster smarter JavaScript debugging in Firefox DevTools', topic_page_article.title)


class TopicsTests(WagtailPageTests):
    """Tests for the Topics page model."""

    fixtures = ['common.json']

    def test_topics__page_parent_pages(self):
        """The Topics page can exist under another page."""
        self.assertAllowedParentPageTypes(Topics, {HomePage})

    def test_topics_page_subpages(self):
        """The Topics page should only have topic child pages."""
        self.assertAllowedSubpageTypes(Topics, {Topic})
