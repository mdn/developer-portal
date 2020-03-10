from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...home.models import HomePage
from ...people.models import People
from ...topics.models import Topic
from ..models import ContentPage


class ContentPageTests(PatchedWagtailPageTests):
    """Tests for the ContentPage model."""

    def test_content_page_parent_pages(self):
        self.assertAllowedParentPageTypes(ContentPage, {ContentPage, HomePage, Topic})

    def test_content_page_subpages(self):
        self.assertAllowedSubpageTypes(ContentPage, {ContentPage, People})
