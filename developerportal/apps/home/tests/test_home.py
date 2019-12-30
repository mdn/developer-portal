from wagtail.core.models import Page

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...articles.models import Articles
from ...content.models import ContentPage
from ...events.models import Events
from ...people.models import People
from ...topics.models import Topic, Topics
from ...videos.models import Videos
from ..models import HomePage


class HomePageTests(PatchedWagtailPageTests):
    """Tests for the HomePage model."""

    fixtures = ["common.json"]

    def test_topic_parent_pages(self):
        self.assertAllowedParentPageTypes(HomePage, {Page})

    def test_home_page_subpages(self):
        self.assertAllowedSubpageTypes(
            HomePage, {Articles, ContentPage, Events, Topics, People, Videos}
        )

    def test_topics_list_gets_only_desired_topics(self):

        home_page = HomePage.objects.get()
        initial_topics_from_page = home_page.primary_topics
        assert all([x.show_in_list_views for x in initial_topics_from_page])

        topic = Topic.objects.first()
        topic.show_in_list_views = False
        topic.save()

        updated_topics_from_page = home_page.primary_topics
        assert all([x.show_in_list_views for x in updated_topics_from_page])
        assert updated_topics_from_page.count() == initial_topics_from_page.count() - 1
