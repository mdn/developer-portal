from django.test import TestCase
from django.urls import reverse

from ...common.constants import SEARCH_QUERYSTRING_KEY


class SearchViewsTests(TestCase):

    fixtures = ["common_plus_extras_for_search_tests.json"]

    def setUp(self):
        self.search_url = reverse("search.site_search")

    def test_site_search_page_fundamentals(self):
        "Light test of site search view's inputs and outputs"

        # no authentication needed
        resp = self.client.get(self.search_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed("search/site-search.html")
        self.assertEqual(resp.context["search_query"], None)
        self.assertEqual(resp.context["total_results"], 0)
        self.assertEqual(len(resp.context["search_results"]), 0)

    def test_site_search_page__search_execution(self):
        "Light test of search hits, misses and single results"
        cases = (
            ("Mozilla Developer Roadshow", [12, 37, 38]),
            ("Nothing will match this", []),
            ("flexbox vs css Grid", [19]),  # Single hit + case insensitivity
        )
        for case in cases:
            with self.subTest(case=case):

                search_params = case[0]
                expected_page_ids = case[1]

                url = f"{self.search_url}?{SEARCH_QUERYSTRING_KEY}={search_params}"

                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.context["search_query"], search_params)
                self.assertEqual(resp.context["total_results"], len(expected_page_ids))
                self.assertEqual(
                    sorted([x.id for x in resp.context["search_results"]]),
                    expected_page_ids,
                )
