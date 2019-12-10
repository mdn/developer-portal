from django.db.models import Q
from django.test import TestCase

from ..utils import build_complex_filtering_query_from_query_params, paginate_resources


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

    def test_paginate_resources__multiple_pages(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=2)
        self.assertEqual(repr(resources), "<Page 2 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(11, 21)])

    def test_paginate_resources__out_of_range(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=2342343243)
        self.assertEqual(repr(resources), "<Page 3 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(21, 26)])

    def test_paginate_resources__default(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref=None)
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])

    def test_paginate_resources__not_an_integer(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref="test")
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])

    def test_paginate_resources__empty_string(self):
        resources = [x for x in range(1, 26)]  # [1... 25]
        resources = paginate_resources(resources, per_page=10, page_ref="")
        self.assertEqual(repr(resources), "<Page 1 of 3>")
        self.assertEqual([x for x in resources], [x for x in range(1, 11)])
