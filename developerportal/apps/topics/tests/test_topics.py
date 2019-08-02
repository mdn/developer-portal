from wagtail.tests.utils import WagtailPageTests

from ..models import Topic, Topics
from ...home.models import HomePage


class TopicsFixturesMixin():
    fixtures = [
        'topics.json',
        'articles.json',
        'people.json',
    ]


class TopicTests(TopicsFixturesMixin, WagtailPageTests):
    """Tests for the Topic page model."""

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
        self.assertEqual('Developer Roadshow 2019 returns with VR, IoT and all things web', topic_page_article.title)


class TopicsTests(TopicsFixturesMixin, WagtailPageTests):
    """Tests for the Topics page model."""

    def test_topics__page_parent_pages(self):
        """The Topics page can exist under another page."""
        self.assertAllowedParentPageTypes(Topics, {HomePage})

    def test_topics_page_subpages(self):
        """The Topics page should only have topic child pages."""
        self.assertAllowedSubpageTypes(Topics, {Topic})
