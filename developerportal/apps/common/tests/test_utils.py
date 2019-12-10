from django.db.models import Q
from django.test import TestCase

from ..utils import build_complex_filtering_query_from_query_params


class HelperFunctionTests(TestCase):
    def test_build_complex_filtering_query_from_query_params__no_params(self):

        cases = ([""], "", [], None)

        for params in cases:
            with self.subTest(params=params):
                output = build_complex_filtering_query_from_query_params(
                    query_syntax="foo__bar", params=params
                )
                self.assertIsNone(output)

    def test_build_complex_filtering_query_from_query_params__single_param(self):

        output = build_complex_filtering_query_from_query_params(
            query_syntax="foo__bar", params=["test"]
        )
        expected = Q(foo__bar="test")
        self.assertEqual(output, expected)

    def test_build_complex_filtering_query_from_query_params__multiple_params(self):

        output = build_complex_filtering_query_from_query_params(
            query_syntax="foo__bar", params=["test", "javascript"]
        )
        expected_q = Q(foo__bar="test")
        expected_q.add(Q(foo__bar="javascript"), Q.OR)
        self.assertEqual(output, expected_q)
