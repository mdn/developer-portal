from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import SubTopic, Topic, Topics


class TopicTests(WagtailPageTests):
    """Tests for the Topic page model."""

    def test_topic_parent_pages(self):
        self.assertAllowedParentPageTypes(Topic, {Topics})

    def test_topic_subpages(self):
        self.assertAllowedSubpageTypes(Topic, {SubTopic})


class SubTopicTests(WagtailPageTests):
    """Tests for the Topic page model."""

    def test_subtopic_parent_pages(self):
        self.assertAllowedParentPageTypes(SubTopic, {Topic})

    def test_subtopic_subpages(self):
        self.assertAllowedSubpageTypes(SubTopic, {})


class TopicsTests(WagtailPageTests):
    """Tests for the Topics page model."""

    def test_topics_parent_pages(self):
        self.assertAllowedParentPageTypes(Topics, {Page})

    def test_topics_subpages(self):
        self.assertAllowedSubpageTypes(Topics, {Topic})
