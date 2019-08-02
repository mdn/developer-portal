from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import HomePage
from ...articles.models import Articles
from ...content.models import ContentPage
from ...events.models import Events
from ...topics.models import Topics
from ...people.models import People


class HomePageTests(WagtailPageTests):
    """Tests for the HomePage model."""

    def test_topic_parent_pages(self):
        self.assertAllowedParentPageTypes(HomePage, {Page})

    def test_home_page_subpages(self):
        self.assertAllowedSubpageTypes(HomePage, {Articles, ContentPage, Events, Topics, People})
