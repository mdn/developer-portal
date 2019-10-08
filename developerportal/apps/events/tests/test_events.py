import datetime

from wagtail.tests.utils import WagtailPageTests

from ...home.models import HomePage
from ..models import Event, Events


class EventTests(WagtailPageTests):
    """Tests for the Event model."""

    def test_event_parent_pages(self):
        self.assertAllowedParentPageTypes(Event, {Events})

    def test_event_subpages(self):
        self.assertAllowedSubpageTypes(Event, {})


class EventsTests(WagtailPageTests):
    """Tests for the Events model."""

    fixtures = ["common.json"]

    def test_events_parent_pages(self):
        self.assertAllowedParentPageTypes(Events, {HomePage})

    def test_events_subpages(self):
        self.assertAllowedSubpageTypes(Events, {Event})

    def test_events_upcoming_events(self):
        events_page = Events.published_objects.first()
        now = datetime.datetime.now()

        event_today = Event(depth=2, path="00019998", start_date=now, title="Today")
        event_today.save()

        event_tomorrow = Event(
            depth=2,
            path="00019999",
            start_date=now + datetime.timedelta(days=1),
            title="Tomorrow",
        )
        event_tomorrow.save()

        event_yesterday = Event(
            depth=2,
            path="00019997",
            start_date=now + datetime.timedelta(days=-1),
            title="Yesterday",
        )
        event_yesterday.save()

        events = events_page.events
        self.assertIn(event_today, events)
        self.assertIn(event_tomorrow, events)
        self.assertNotIn(event_yesterday, events)
