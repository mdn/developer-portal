from unittest import mock

from django.test import TestCase

from ...content.models import ContentPage


class PageBaseModelTestsUsingConcreteClass(TestCase):
    """Tests that use a concrete ContentPage class to test behaviour
    from the BasePage"""

    def test_save(self):

        with mock.patch(
            "developerportal.apps.common.models.cache.delete_many"
        ) as mock_delete_many:

            self.assertEqual(ContentPage._bulk_invalidation_cache_keys, [])

            page = ContentPage(slug="test", path="00010022", depth=2, title="Test")
            page._bulk_invalidation_cache_keys = ["foo", "bar", "baz"]
            page.save()
            mock_delete_many.assert_called_once_with(["foo", "bar", "baz"])
