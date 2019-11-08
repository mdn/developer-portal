from django.test import TestCase

from wagtail.core.models import Page

from developerportal.templatetags.app_tags import has_at_least_two_filters


class AppTagsTestCase(TestCase):
    def test_has_at_least_two_filters(self):

        case_data = [
            # One item
            ({"foos": Page.objects.none()}, False),
            ({"foos": Page.objects.all()}, False),
            # Two items
            ({"foos": Page.objects.none(), "bars": True}, False),
            ({"foos": Page.objects.none(), "bars": False}, False),
            ({"foos": Page.objects.all(), "bars": True}, True),
            ({"foos": Page.objects.all(), "bars": False}, False),
            # Three items
            ({"foos": Page.objects.none(), "bars": True, "bams": True}, True),
            ({"foos": Page.objects.none(), "bars": False, "bams": True}, False),
            ({"foos": Page.objects.none(), "bars": False, "bams": False}, False),
            ({"foos": Page.objects.all(), "bars": True, "bams": True}, True),
            ({"foos": Page.objects.all(), "bars": False, "bams": True}, True),
            ({"foos": Page.objects.all(), "bars": False, "bams": False}, False),
        ]
        for data, expected_outcome in case_data:
            with self.subTest(data=data, expected_outcome=expected_outcome):
                self.assertEqual(has_at_least_two_filters(data), expected_outcome)
