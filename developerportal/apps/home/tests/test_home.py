from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import HomePage
from ...content.models import ContentPage


class HomePageTests(WagtailPageTests):
    """Tests for the HomePage model."""

    def test_topic_parent_pages(self):
        self.assertAllowedParentPageTypes(HomePage, {Page})

    def test_home_page_subpages(self):
        self.assertAllowedSubpageTypes(HomePage, {ContentPage})
