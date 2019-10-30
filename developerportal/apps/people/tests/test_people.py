from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...content.models import ContentPage
from ...home.models import HomePage
from ..models import People, Person


class PersonTests(PatchedWagtailPageTests):
    """Tests for the Person model."""

    def test_person_parent_pages(self):
        self.assertAllowedParentPageTypes(Person, {People})

    def test_person_subpages(self):
        self.assertAllowedSubpageTypes(Person, {})


class PeopleTests(PatchedWagtailPageTests):
    """Tests for the People model."""

    def test_people_parent_pages(self):
        self.assertAllowedParentPageTypes(People, {HomePage, ContentPage})

    def test_people_subpages(self):
        self.assertAllowedSubpageTypes(People, {Person})
