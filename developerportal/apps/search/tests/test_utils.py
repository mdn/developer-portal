from django.core.cache import cache
from django.test import TestCase

from ..utils import PAGE_IDS_TO_EXCLUDE_CACHE_KEY, get_page_ids_to_omit_from_site_search


class SearchUtilsTests(TestCase):

    fixtures = ["common_plus_extras_for_search_tests.json"]

    def setUp(self):

        ARTICLES_PAGE_ID = 4
        EVENTS_PAGE_ID = 33
        HOMEPAGE_PAGE_ID = 3
        PEOPLE_PAGE_ID = 9
        TOPICS_PAGE_ID = 5
        VIDEOS_PAGE_ID = 36

        self.ids_to_exclude = sorted(
            [
                ARTICLES_PAGE_ID,
                EVENTS_PAGE_ID,
                HOMEPAGE_PAGE_ID,
                PEOPLE_PAGE_ID,
                TOPICS_PAGE_ID,
                VIDEOS_PAGE_ID,
            ]
        )

        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_get_page_ids_to_omit_from_site_search(self):

        assert get_page_ids_to_omit_from_site_search() == self.ids_to_exclude

    def test_get_page_ids_to_omit_from_site_search__sets_cached_value(self):

        self.assertIsNone(cache.get(PAGE_IDS_TO_EXCLUDE_CACHE_KEY))

        get_page_ids_to_omit_from_site_search()

        self.assertEqual(
            sorted(cache.get(PAGE_IDS_TO_EXCLUDE_CACHE_KEY)), self.ids_to_exclude
        )
