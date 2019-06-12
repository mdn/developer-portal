from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import SubTopic, Topic, Topics
from ...articles.models import Article


class TopicsFixturesMixin():
    fixtures = [
        'topics.json',
        'articles.json',
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
        """A topic page should only have sub-topic child pages."""
        self.assertAllowedSubpageTypes(Topic, {SubTopic})

    def test_topic_page_articles(self):
        """A topic page should have article pages."""
        topic_page = Topic.objects.all()[0]
        article_page = Article.objects.all()[0]
        topic_page_article = topic_page.articles.all()[0].article
        self.assertEqual(article_page, topic_page_article)

    def test_topic_page_featured_articles(self):
        """A topic page should have featured article pages."""
        topic_page = Topic.objects.all()[0]
        featured_article_pages = topic_page.featured_articles.all()
        self.assertCountEqual([], featured_article_pages)


class SubTopicTests(WagtailPageTests):
    """Tests for the Topic page model."""

    def test_subtopic_page_parent_pages(self):
        """A sub-topic page should only exist under a topic page."""
        self.assertAllowedParentPageTypes(SubTopic, {Topic})

    def test_subtopic_page_subpages(self):
        """A sub-topic page should not have child pages."""
        self.assertAllowedSubpageTypes(SubTopic, {})


class TopicsTests(TopicsFixturesMixin, WagtailPageTests):
    """Tests for the Topics page model."""

    def test_topics__page_parent_pages(self):
        """The Topics page can exist under another page."""
        self.assertAllowedParentPageTypes(Topics, {Page})

    def test_topics_page_subpages(self):
        """The Topics page should only have topic child pages."""
        self.assertAllowedSubpageTypes(Topics, {Topic})
