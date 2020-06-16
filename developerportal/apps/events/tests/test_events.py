import datetime
from unittest import mock

from django.db.models import Q
from django.test import RequestFactory

import pytz
from dateutil.relativedelta import relativedelta

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...common.constants import (
    DATE_PARAMS_QUERYSTRING_KEY,
    DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS,
    FUTURE_EVENTS_QUERYSTRING_VALUE,
    PAST_EVENTS_QUERYSTRING_VALUE,
)
from ...home.models import HomePage
from ..models import Event, Events


class EventTests(PatchedWagtailPageTests):
    """Tests for the Event Page."""

    def test_event_parent_pages(self):
        self.assertAllowedParentPageTypes(Event, {Events})

    def test_event_subpages(self):
        self.assertAllowedSubpageTypes(Event, {})

    def test_summary_meta(self):

        start_date = datetime.datetime(2020, 3, 5)

        cases = (
            {
                "input": {"path": "00019998", "country": "", "city": ""},
                "output": "Mar 5",
            },
            {
                "input": {"path": "00019997", "country": "FR", "city": ""},
                "output": "Mar 5 | FR",
            },
            {
                "input": {"path": "00019995", "country": "FR", "city": "Paris"},
                "output": "Mar 5 | Paris, FR",
            },
        )

        for case in cases:
            with self.subTest(case=case):
                event = Event(
                    depth=2, start_date=start_date, title="Test", **case["input"]
                )
                event.save()
                self.assertEqual(event.summary_meta, case["output"])


class EventsTests(PatchedWagtailPageTests):
    """Tests for the Events Page."""

    fixtures = ["common.json"]

    def test_events_parent_pages(self):
        self.assertAllowedParentPageTypes(Events, {HomePage})

    def test_events_subpages(self):
        self.assertAllowedSubpageTypes(Events, {Event})

    def test_page_functions_with_search_params(self):
        # If search is misconfigured, this will 500
        response = self.client.get("/events/?search=test")
        assert response.status_code == 200

    def test_events_get_events(self):
        # General test - more specific ones for the Qs are below.
        # These all fall into the "next X months" default view
        events_page = Events.published_objects.first()
        now = datetime.datetime.now()

        request = RequestFactory().get("/")

        event_today = Event(depth=2, path="00019998", start_date=now, title="Today")
        event_today.save()

        event_tomorrow = Event(
            depth=2,
            path="00019999",
            start_date=now + datetime.timedelta(days=1),
            title="Tomorrow",
        )
        event_tomorrow.save()

        event_in_n_months_plus_one_day = Event(
            depth=2,
            path="00019399",
            start_date=now
            + relativedelta(months=DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS, days=1),
            title="Event in one day less than N months",
        )
        event_in_n_months_plus_one_day.save()

        event_in_n_months = Event(
            depth=2,
            path="00019499",
            start_date=now
            + relativedelta(months=DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS),
            title="Event in N months",
        )
        event_in_n_months.save()

        event_yesterday = Event(
            depth=2,
            path="00019997",
            start_date=now - datetime.timedelta(days=1),
            title="Yesterday",
        )
        event_yesterday.save()

        event_day_before_yesterday = Event(
            depth=2,
            path="00019992",
            start_date=now - datetime.timedelta(days=2),
            title="Day Before Yesterday",
        )
        event_day_before_yesterday.save()

        events = events_page.get_events(request)
        self.assertIn(event_today, events)
        self.assertIn(event_tomorrow, events)
        self.assertIn(event_in_n_months, events)
        self.assertIn(event_yesterday, events)  # CORRECT
        self.assertNotIn(event_day_before_yesterday, events)  # CORRECT
        self.assertNotIn(event_in_n_months_plus_one_day, events)

    @mock.patch("developerportal.apps.events.models.paginate_resources")
    def test_events_get_events__paginates(self, mock_paginate_resources):
        events_page = Events.published_objects.first()
        request = RequestFactory().get("/")
        events_page.get_events(request)
        assert mock_paginate_resources.called

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__no_params(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get("/")

        expected_q = Q(
            start_date__gte=datetime.date(2022, 10, 3),
            start_date__lte=datetime.date(2023, 4, 4),
        )  # default restrictions

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms=None, reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__all_params_except_date_ones(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz&search=test+event"
        )

        # Build the query we expect to be generated
        # no date params past means everything for the next X months
        overall_date_q = Q(
            start_date__gte=datetime.date(2022, 10, 3),
            start_date__lte=datetime.date(2023, 4, 4),
        )

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms="test event", reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__filters__no_dates__no_search(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
        )

        # Build the query we expect to be generated
        # no date params past means everything for the next X months
        overall_date_q = Q(
            start_date__gte=datetime.date(2022, 10, 3),
            start_date__lte=datetime.date(2023, 4, 4),
        )

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms=None, reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__all_params_including_past_events(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={PAST_EVENTS_QUERYSTRING_VALUE}"
                "&search=another+test+event"
            )
        )

        # Add the Q that INCLUDES all past events
        overall_date_q = Q(start_date__lte=datetime.date(2022, 10, 3))

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page,
            q_object=expected_q,
            search_terms="another test event",
            reverse=False,
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__filters_and_past_events__no_search(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={PAST_EVENTS_QUERYSTRING_VALUE}"
            )
        )

        # Add the Q that INCLUDES all past events
        overall_date_q = Q(start_date__lte=datetime.date(2022, 10, 3))

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms=None, reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__all_params_including_future_events(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={FUTURE_EVENTS_QUERYSTRING_VALUE}"
                f"&search=test+here"
            )
        )

        # Add the Q that INCLUDES all future events
        overall_date_q = Q(start_date__gte=datetime.date(2022, 10, 3))

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms="test here", reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__filters_and_future_events__no_search(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={FUTURE_EVENTS_QUERYSTRING_VALUE}"
            )
        )

        # Add the Q that INCLUDES all future events
        overall_date_q = Q(start_date__gte=datetime.date(2022, 10, 3))

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms=None, reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__all_params_including_past_and_future_events(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        # So we show all events
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={PAST_EVENTS_QUERYSTRING_VALUE}"
                f"&date={FUTURE_EVENTS_QUERYSTRING_VALUE}"
                f"&search=another+test+query"
            )
        )

        # Add the Q that INCLUDES ALL event dates
        overall_date_q = Q()

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page,
            q_object=expected_q,
            search_terms="another test query",
            reverse=False,
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__filters_and_past_and_future_events__no_search(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        # So we show all events
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                f"&date={PAST_EVENTS_QUERYSTRING_VALUE}"
                f"&date={FUTURE_EVENTS_QUERYSTRING_VALUE}"
            )
        )

        # Add the Q that INCLUDES ALL event dates
        overall_date_q = Q()

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, search_terms=None, reverse=False
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__default_only(self, mock_get_past_event_cutoff):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(date_params=[""])

        expected_q = Q(
            start_date__gte=datetime.date(2022, 10, 3),
            start_date__lte=datetime.date(2023, 4, 4),
        )
        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__past_events_specified(self, mock_get_past_event_cutoff):

        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            date_params=[PAST_EVENTS_QUERYSTRING_VALUE]
        )

        expected_q = Q(start_date__lte=datetime.date(2022, 10, 3))

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__future_events_specified(self, mock_get_past_event_cutoff):

        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            date_params=[FUTURE_EVENTS_QUERYSTRING_VALUE]
        )

        expected_q = Q(start_date__gte=datetime.date(2022, 10, 3))

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__both_past_and_future_events_selected(
        self, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            date_params=[FUTURE_EVENTS_QUERYSTRING_VALUE, PAST_EVENTS_QUERYSTRING_VALUE]
        )

        # build the expected result for comparison
        date_q = Q()  #  no date filtering -> show all events

        expected_q = date_q

        self.assertEqual(output_q, expected_q)

    def test_get_event_date_options(self):

        cases = (
            {
                "querystring": f"{DATE_PARAMS_QUERYSTRING_KEY}={PAST_EVENTS_QUERYSTRING_VALUE}",  # noqa E501
                "expected": {
                    "options_selected": True,
                    "options": [
                        {
                            "value": PAST_EVENTS_QUERYSTRING_VALUE,
                            "label": "Past events",
                        },
                        {
                            "value": FUTURE_EVENTS_QUERYSTRING_VALUE,
                            "label": "Future events",
                        },
                    ],
                },
            },
            {
                "querystring": f"{DATE_PARAMS_QUERYSTRING_KEY}={FUTURE_EVENTS_QUERYSTRING_VALUE}",  # noqa E501
                "expected": {
                    "options_selected": True,
                    "options": [
                        {
                            "value": PAST_EVENTS_QUERYSTRING_VALUE,
                            "label": "Past events",
                        },
                        {
                            "value": FUTURE_EVENTS_QUERYSTRING_VALUE,
                            "label": "Future events",
                        },
                    ],
                },
            },
            {
                "querystring": (
                    f"{DATE_PARAMS_QUERYSTRING_KEY}={PAST_EVENTS_QUERYSTRING_VALUE}&"
                    f"{DATE_PARAMS_QUERYSTRING_KEY}={FUTURE_EVENTS_QUERYSTRING_VALUE}"
                ),
                "expected": {
                    "options_selected": True,
                    "options": [
                        {
                            "value": PAST_EVENTS_QUERYSTRING_VALUE,
                            "label": "Past events",
                        },
                        {
                            "value": FUTURE_EVENTS_QUERYSTRING_VALUE,
                            "label": "Future events",
                        },
                    ],
                },
            },
            {
                "querystring": "",
                "expected": {
                    "options_selected": False,
                    "options": [
                        {
                            "value": PAST_EVENTS_QUERYSTRING_VALUE,
                            "label": "Past events",
                        },
                        {
                            "value": FUTURE_EVENTS_QUERYSTRING_VALUE,
                            "label": "Future events",
                        },
                    ],
                },
            },
        )
        for case in cases:
            with self.subTest(case=case):
                fake_request = RequestFactory().get(f"/?{case['querystring']}")
                events_page = Events.published_objects.first()
                options = events_page.get_event_date_options(fake_request)
                self.assertEqual(options, case["expected"])

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test_events__get_relevant_countries(self, mock_get_past_event_cutoff):

        _now = datetime.datetime(2022, 10, 3, 12, 34, 56, tzinfo=pytz.utc)
        mock_get_past_event_cutoff.return_value = _now

        events_page = Events.published_objects.first()
        events_page.add_child(
            instance=Event(
                depth=2, path="00019998", start_date=_now, title="A", country="GB"
            )
        )

        events_page.add_child(
            instance=Event(
                depth=2, path="00019999", start_date=_now, title="B", country="DE"
            )
        )

        # event_next_year
        events_page.add_child(
            instance=Event(
                depth=2, path="00019929", start_date=_now, title="C", country="US"
            )
        )

        events_page.add_child(
            instance=Event(
                depth=2, path="00019989", start_date=_now, title="D", country="GB"
            )
        )

        events_page.add_child(
            instance=Event(
                depth=2, path="00019997", start_date=_now, title="E", country="AR"
            )
        )
        events_page.add_child(
            instance=Event(
                depth=2,
                path="00019997",
                start_date=_now - datetime.timedelta(days=9999),
                title="E",
                country="ZA",
            )
        )
        expected = [
            {"code": "AR", "name": "Argentina"},
            {"code": "DE", "name": "Germany"},
            {"code": "GB", "name": "United Kingdom"},  # only one appearance is correct
            {"code": "US", "name": "United States of America"},
            {"code": "ZA", "name": "South Africa"},  # from a past event
        ]
        actual = events_page.get_relevant_countries()
        self.assertEqual(actual, expected)
