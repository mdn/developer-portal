from unittest import mock

from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse


class HealthTestCases(TestCase):
    """Tests for the health-check endpoints."""

    def test_disallowed_methods(self):
        """Test the endpoints using the disallowed HTTP methods."""
        for endpoint in ('liveness', 'readiness'):
            url = reverse('health.{}'.format(endpoint))
            for method in ('put', 'post', 'delete', 'options'):
                with self.subTest(endpoint=endpoint, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(response.status_code, 405)

    def test_safe_methods(self):
        """Test the endpoints using the safe HTTP methods."""
        for endpoint in ('liveness', 'readiness'):
            url = reverse('health.{}'.format(endpoint))
            for method in ('get', 'head'):
                with self.subTest(endpoint=endpoint, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(response.status_code, 204)

    def test_readiness_with_db_error(self):
        """Test the readiness endpoint when there is a database issue."""
        url = reverse('health.readiness')
        article_model_mgr = 'developerportal.apps.health.views.Article.objects'
        with mock.patch(article_model_mgr) as mocked:
            mocked.filter.side_effect = DatabaseError('fubar')
            for method in ('get', 'head'):
                with self.subTest(method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(response.status_code, 503)
                    self.assertTrue('fubar' in response.reason_phrase)
