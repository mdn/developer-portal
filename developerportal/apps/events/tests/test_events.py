import datetime
from unittest import mock

from django.db.models import Q
from django.test import RequestFactory

import pytz

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...common.constants import PAST_EVENTS_QUERYSTRING_VALUE
from ...home.models import HomePage
from ..models import Event, Events


class EventTests(PatchedWagtailPageTests):
    """Tests for the Event model."""

    def test_event_parent_pages(self):
        self.assertAllowedParentPageTypes(Event, {Events})

    def test_event_subpages(self):
        self.assertAllowedSubpageTypes(Event, {})


class EventsTests(PatchedWagtailPageTests):
    """Tests for the Events model."""

    fixtures = ["common.json"]

    def test_events_parent_pages(self):
        self.assertAllowedParentPageTypes(Events, {HomePage})

    def test_events_subpages(self):
        self.assertAllowedSubpageTypes(Events, {Event})

    def test_events_get_events(self):
        # General test - more specific ones for the Qs are below
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
        # Default request is __all__ events, 8 per page
        self.assertIn(event_today, events)
        self.assertIn(event_tomorrow, events)
        self.assertIn(event_yesterday, events)  # CORRECT
        self.assertIn(event_day_before_yesterday, events)  # CORRECT

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

        expected_q = Q()  # no restrictions
        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, reverse=True
        )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    @mock.patch("developerportal.apps.events.models.get_combined_events")
    def test_events__get_events__query__all_params_except_past_events(
        self, mock_get_combined_events, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)

        events_page = Events.published_objects.first()
        fake_request = RequestFactory().get(
            (
                "/?country=CA&country=ZA&topic=foo&topic=bar&topic=baz"
                "&date=2020-02&date=2020-03"
            )
        )

        date_q1 = Q(start_date__year="2020")
        date_q1.add(Q(start_date__month="02"), Q.AND)

        date_q2 = Q(start_date__year="2020")
        date_q2.add(Q(start_date__month="03"), Q.AND)

        overall_date_q = date_q1
        overall_date_q.add(date_q2, Q.OR)
        # Add the Q that stops past events for the selected month
        overall_date_q.add(Q(start_date__gte=datetime.date(2022, 10, 3)), Q.AND)

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, reverse=True
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
                f"&date=2020-02&date=2020-03&date={PAST_EVENTS_QUERYSTRING_VALUE}"
            )
        )

        date_q1 = Q(start_date__year="2020")
        date_q1.add(Q(start_date__month="02"), Q.AND)

        date_q2 = Q(start_date__year="2020")
        date_q2.add(Q(start_date__month="03"), Q.AND)

        overall_date_q = date_q1
        overall_date_q.add(date_q2, Q.OR)

        # Add the Q that INCLUDES all past events
        overall_date_q.add(Q(start_date__lte=datetime.date(2022, 10, 3)), Q.OR)

        countries_q = Q(country__in=["CA", "ZA"])
        topics_q = Q(topics__topic__slug__in=["foo", "bar", "baz"])

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(overall_date_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        events_page.get_events(fake_request)
        mock_get_combined_events.assert_called_once_with(
            events_page, q_object=expected_q, reverse=True
        )

    def test_year_months_to_years_and_months_tuples(self):
        events_page = Events()

        cases = (
            {"in": "", "out": []},
            {"in": [""], "out": []},
            {"in": [None], "out": []},
            {"in": None, "out": []},
            {"in": ["2019-10"], "out": [("2019", "10")]},
            {"in": ["2019-10", "2022-03"], "out": [("2019", "10"), ("2022", "03")]},
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    events_page._year_months_to_years_and_months_tuples(case["in"]),
                    case["out"],
                )

    def test_pop_past_events_marker_from_date_params(self):
        events_page = Events()

        cases = (
            {"in": "", "out": ("", False)},
            {"in": [""], "out": ([""], False)},
            {"in": [None], "out": ([None], False)},
            {"in": None, "out": (None, False)},
            {"in": ["2019-10"], "out": (["2019-10"], False)},
            {"in": ["2019-10", "2022-03"], "out": (["2019-10", "2022-03"], False)},
            {
                "in": ["2019-10", "2022-03", "past"],
                "out": (["2019-10", "2022-03"], True),
            },
            {
                "in": ["2019-10", "past", "2022-03"],
                "out": (["2019-10", "2022-03"], True),
            },
            {
                "in": ["past", "2019-10", "2022-03"],
                "out": (["2019-10", "2022-03"], True),
            },
            {"in": ["past"], "out": ([], True)},
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    events_page._pop_past_events_marker_from_date_params(case["in"]),
                    case["out"],
                )

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__default_only(self, mock_get_past_event_cutoff):

        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            # self.test_year_months_to_years_and_months_tuples() shows that this
            # equates to no parameter-based filtering
            date_params=[""]
        )

        expected_q = Q()  # Just an empty Q with no date filtering at all

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__past_events_specified(self, mock_get_past_event_cutoff):

        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            # self.test_year_months_to_years_and_months_tuples() shows that this
            # equates to no parameter-based filtering
            date_params=["past"]
        )

        expected_q = Q(start_date__lte=datetime.date(2022, 10, 3))

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__has_one_date_pair_and_no_past_events(
        self, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(
            date_params=[
                "2023-10"
                # This has to be after mock_get_past_event_cutoff,
                # else it won't show
            ]
        )

        # build the expected result for comparison
        date_q = Q(start_date__year="2023")
        date_q.add(Q(start_date__month="10"), Q.AND)

        expected_q = date_q
        # Add the Q that stops past events for the selected month
        expected_q.add(Q(start_date__gte=datetime.date(2022, 10, 3)), Q.AND)

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__has_one_date_pair_and_past_events_specified(
        self, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()

        output_q = events_page._build_date_q(date_params=["2023-10", "past"])

        # build the expected result for comparison
        date_q = Q(start_date__year="2023")
        date_q.add(Q(start_date__month="10"), Q.AND)

        expected_q = date_q
        # Add the Q that INCLUDES all past events
        expected_q.add(Q(start_date__lte=datetime.date(2022, 10, 3)), Q.OR)

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__has_multiple_date_pairs_and_no_past_events(
        self, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()
        output_q = events_page._build_date_q(
            date_params=[
                "2024-03",
                "2023-10",
                # These have to be after mock_get_past_event_cutoff,
                # else they won't show
            ]
        )

        # build the expected result for comparison
        date_q1 = Q(start_date__year="2024")
        date_q1.add(Q(start_date__month="03"), Q.AND)

        date_q2 = Q(start_date__year="2023")
        date_q2.add(Q(start_date__month="10"), Q.AND)

        expected_q = date_q1
        expected_q.add(date_q2, Q.OR)
        # Add the Q that stops past events for the selected month
        expected_q.add(Q(start_date__gte=datetime.date(2022, 10, 3)), Q.AND)

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test__build_date_q__has_multiple_date_pairs_and_past_events_specified(
        self, mock_get_past_event_cutoff
    ):
        mock_get_past_event_cutoff.return_value = datetime.date(2022, 10, 3)
        events_page = Events()
        output_q = events_page._build_date_q(date_params=["2024-03", "2023-10", "past"])

        # build the expected result for comparison
        date_q1 = Q(start_date__year="2024")
        date_q1.add(Q(start_date__month="03"), Q.AND)

        date_q2 = Q(start_date__year="2023")
        date_q2.add(Q(start_date__month="10"), Q.AND)

        expected_q = date_q1
        expected_q.add(date_q2, Q.OR)
        # Add the Q that INCLUDES all past events
        expected_q.add(Q(start_date__lte=datetime.date(2022, 10, 3)), Q.OR)

        self.assertEqual(output_q, expected_q)

    @mock.patch("developerportal.apps.events.models.get_past_event_cutoff")
    def test_events__get_relevant_dates(self, mock_get_past_event_cutoff):

        _now = datetime.datetime(2022, 10, 3, 12, 34, 56, tzinfo=pytz.utc)
        mock_get_past_event_cutoff.return_value = _now

        events_page = Events.published_objects.first()
        events_page.add_child(
            instance=Event(depth=2, path="00019998", start_date=_now, title="Today")
        )

        events_page.add_child(
            instance=Event(
                depth=2,
                path="00019999",
                start_date=_now + datetime.timedelta(days=30),  # So 2022-11-02
                title="Next month",
            )
        )

        # event_next_year
        events_page.add_child(
            instance=Event(
                depth=2,
                path="00019929",
                start_date=_now + datetime.timedelta(days=365),  # So 2023-10-03
                title="Next year",
            )
        )

        events_page.add_child(
            instance=Event(
                depth=2,
                path="00019989",
                start_date=_now + datetime.timedelta(days=7),  # So 2022-10-10
                title="Next week",
            )
        )

        events_page.add_child(
            instance=Event(
                depth=2,
                path="00019997",
                start_date=_now + datetime.timedelta(days=-1),  # So 2022-10-02
                title="Yesterday",
                # THIS ONE SHOULD NOT FEATURE IN THE RESULTS
            )
        )
        expected = [
            datetime.date(2022, 10, 3),
            datetime.date(2022, 10, 10),
            datetime.date(2022, 11, 2),
            datetime.date(2023, 10, 3),
        ]
        actual = events_page.get_relevant_dates()
        self.assertEqual(actual, expected)

    def test_dates_to_unique_month_years(self):
        cases = [
            {
                "input": [
                    datetime.date(2022, 10, 3),
                    datetime.date(2022, 10, 10),
                    datetime.date(2022, 11, 2),
                    datetime.date(2022, 10, 3),  # Same as first date
                ],
                "expected": [datetime.date(2022, 11, 1), datetime.date(2022, 10, 1)],
            },
            {
                "input": [
                    datetime.date(2022, 10, 3),
                    datetime.date(2022, 10, 10),
                    datetime.date(2023, 12, 3),
                    datetime.date(2022, 11, 2),
                ],
                "expected": [
                    datetime.date(2023, 12, 1),
                    datetime.date(2022, 11, 1),
                    datetime.date(2022, 10, 1),
                ],
            },
            {
                "input": [
                    datetime.date(2022, 10, 3),
                    datetime.date(2023, 12, 3),
                    datetime.date(2022, 11, 2),
                ],
                "expected": [
                    datetime.date(2023, 12, 1),
                    datetime.date(2022, 11, 1),
                    datetime.date(2022, 10, 1),
                ],
            },
            {
                "input": [
                    datetime.date(2023, 12, 3),
                    datetime.date(2023, 12, 3),
                    datetime.date(2023, 12, 3),
                ],
                "expected": [datetime.date(2023, 12, 1)],
            },
        ]
        for case in cases:
            with self.subTest(case=case):
                actual = Events().dates_to_unique_month_years(case["input"])
                self.assertEqual(actual, case["expected"])

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
