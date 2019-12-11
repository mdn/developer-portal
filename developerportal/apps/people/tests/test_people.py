from unittest import mock

from django.db.models import Q
from django.test import RequestFactory

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

    @mock.patch("developerportal.apps.people.models.paginate_resources")
    @mock.patch("developerportal.apps.people.models.Person.published_objects.filter")
    def test_get_people__filtering_and_pagination_called(
        self, mock_filter, mock_paginate_resources
    ):
        mock_filter.return_value = Person.objects.all()  # NBnot mocked

        request = RequestFactory().get(
            "/?topic=foo,bar&country=DE,ZA&role=staff,community"
        )
        people_page = People(
            title="person_page", path="000100010009", depth=5, slug="people-test"
        )

        people_page.get_people(request)

        assert mock_filter.call_count == 1

        # Can't use assert_called_once_with because one param is a QuerySet,
        # which won't match for equivalency even if they contain the same things
        actual_q = mock_filter.call_args_list[0][0][0]

        countries_q = Q(country="DE")
        countries_q.add(Q(country="ZA"), Q.OR)
        roles_q = Q(role="staff")
        roles_q.add(Q(role="community"), Q.OR)
        topics_q = Q(topics__topic__slug="foo")
        topics_q.add(Q(topics__topic__slug="bar"), Q.OR)

        expected_q = Q()
        expected_q.add(countries_q, Q.AND)
        expected_q.add(roles_q, Q.AND)
        expected_q.add(topics_q, Q.AND)

        self.assertEqual(actual_q, expected_q)

        assert mock_paginate_resources.call_count == 1

        # Can't use assert_called_once_with because one param is a QuerySet,
        # which won't match for equivalency even if they contain the same things
        call_args_list = mock_paginate_resources.call_args_list
        self.assertEqual(list(call_args_list[0][0][0]), list(Person.objects.all()))
        self.assertEqual(call_args_list[0][1]["page_ref"], None)
        self.assertEqual(call_args_list[0][1]["per_page"], People.RESOURCES_PER_PAGE)

    @mock.patch("developerportal.apps.people.models.paginate_resources")
    @mock.patch("developerportal.apps.people.models.Person.published_objects.filter")
    def test_get_people__filtering_variations(
        self, mock_filter, mock_paginate_resources
    ):
        mock_filter.return_value = Person.objects.all()  # NBnot mocked
        people_page = People(
            title="person_page", path="000100010009", depth=5, slug="people-test"
        )

        request = RequestFactory().get("/?topic=foo")
        people_page.get_people(request)
        assert mock_filter.call_count == 1

        actual_q = mock_filter.call_args_list[0][0][0]
        topics_q = Q(topics__topic__slug="foo")
        expected_q = Q()
        expected_q.add(topics_q, Q.AND)
        self.assertEqual(actual_q, expected_q)

        mock_filter.reset_mock()
        request = RequestFactory().get("/?role=staff")
        people_page.get_people(request)
        assert mock_filter.call_count == 1

        actual_q = mock_filter.call_args_list[0][0][0]
        role_q = Q(role="staff")
        expected_q = Q()
        expected_q.add(role_q, Q.AND)
        self.assertEqual(actual_q, expected_q)

        mock_filter.reset_mock()
        request = RequestFactory().get("/?country=UK")
        people_page.get_people(request)
        assert mock_filter.call_count == 1

        actual_q = mock_filter.call_args_list[0][0][0]
        country_q = Q(country="UK")
        expected_q = Q()
        expected_q.add(country_q, Q.AND)
        self.assertEqual(actual_q, expected_q)

    def test_get_relevant_countries(self):
        people_page = People(
            title="person_page", path="000100010009", depth=5, slug="people-test"
        )
        people_page.save()
        people_page.add_child(
            instance=Person(
                title="Person 1",
                job_title="test",
                path="000100020001",
                depth=6,
                country="DE",
                slug="person-1",
            )
        )
        people_page.add_child(
            instance=Person(
                title="Person 2",
                job_title="test",
                path="000100020002",
                depth=6,
                country="CA",
                slug="person-2",
            )
        )
        people_page.add_child(
            instance=Person(
                title="Person 3",
                job_title="test",
                path="000100020003",
                depth=6,
                country="ZA",
                slug="person-3",
            )
        )
        people_page.add_child(
            instance=Person(
                title="Person 4",
                job_title="test",
                path="000100020004",
                depth=6,
                country="DE",  #  ie, a second person in Germany
                slug="person-4",
            )
        )

        output = people_page.get_relevant_countries()
        expected = [
            {"code": "CA", "name": "Canada"},
            {"code": "DE", "name": "Germany"},
            {"code": "ZA", "name": "South Africa"},
        ]

        self.assertEqual(output, expected)
