from wagtail.core.models import Page

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...articles.models import Articles
from ...content.models import ContentPage
from ...events.models import Events
from ...people.models import People
from ...topics.models import Topics
from ...videos.models import Videos
from ..models import HomePage


class HomePageTests(PatchedWagtailPageTests):
    """Tests for the HomePage model."""

    def test_topic_parent_pages(self):
        self.assertAllowedParentPageTypes(HomePage, {Page})

    def test_home_page_subpages(self):
        self.assertAllowedSubpageTypes(
            HomePage, {Articles, ContentPage, Events, Topics, People, Videos}
        )
