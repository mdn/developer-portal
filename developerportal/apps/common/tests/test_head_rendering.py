from django.test import TestCase, override_settings

from developerportal.apps.common.constants import (
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_PRODUCTION,
    ENVIRONMENT_STAGING,
)


class NoIndexMetaTagTests(TestCase):
    def test_noindex_tag_absent_in_production_only(self):
        """Show the <meta> noindex directive for robots is shown on dev and stage
        but not production"""
        cases = [
            {"setting_val": ENVIRONMENT_DEVELOPMENT, "expected": True},
            {"setting_val": ENVIRONMENT_PRODUCTION, "expected": False},
            {"setting_val": ENVIRONMENT_STAGING, "expected": True},
        ]

        for case in cases:
            with self.subTest(case=case):
                with override_settings(ACTIVE_ENVIRONMENT=case["setting_val"]):
                    response = self.client.get("/")
                    if case["expected"]:
                        self.assertContains(
                            response, '<meta name="robots" content="noindex">', 1
                        )
                    else:
                        self.assertNotContains(
                            response,
                            '<meta name="robots" content="noindex">',
                            status_code=200,
                        )
