from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..models import People, Person

class PeopleTests(WagtailPageTests):
    """Tests for the People model."""

    def test_people_parent_pages(self):
        self.assertAllowedParentPageTypes(People, {Page})

    def test_people_subpages(self):
      self.assertAllowedSubpageTypes(People, {Person})

class PersonTests(WagtailPageTests):
    """Tests for the Person model."""

    def test_person_parent_pages(self):
        self.assertAllowedParentPageTypes(Person, {People})

    def test_person_subpages(self):
        self.assertAllowedSubpageTypes(Person, {})

