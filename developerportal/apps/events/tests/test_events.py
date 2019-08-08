from wagtail.tests.utils import WagtailPageTests

from ..models import Event, Events
from ...home.models import HomePage


class EventTests(WagtailPageTests):
    """Tests for the Event model."""

    def test_event_parent_pages(self):
        self.assertAllowedParentPageTypes(Event, {Events})

    def test_event_subpages(self):
        self.assertAllowedSubpageTypes(Event, {})


class EventsTests(WagtailPageTests):
    """Tests for the Events model."""

    def test_events_parent_pages(self):
        self.assertAllowedParentPageTypes(Events, {HomePage})

    def test_events_subpages(self):
        self.assertAllowedSubpageTypes(Events, {Event})
