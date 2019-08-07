from wagtail.tests.utils import WagtailPageTests

from ..models import ContentPage
from ...home.models import HomePage
from ...people.models import People


class ContentPageTests(WagtailPageTests):
    """Tests for the ContentPage model."""

    def test_content_page_parent_pages(self):
        self.assertAllowedParentPageTypes(ContentPage, {ContentPage, HomePage})

    def test_content_page_subpages(self):
        self.assertAllowedSubpageTypes(ContentPage, {ContentPage, People})
