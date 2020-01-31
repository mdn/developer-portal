from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from waffle.models import Flag

from ..constants import WAFFLE_FLAG_TASK_COMPLETION
from ..middleware import (
    request_had_survey_waffle_cookie,
    survey_waffle_flag_cdn_middleware,
    waffle_flag_enabled_with_percentage_rule,
)


class SurveyWaffleFlagCDNMiddlewareTests(TestCase):
    def setUp(self):
        # This flag is created by Migration common.0003
        self.flag = Flag.objects.get(name=WAFFLE_FLAG_TASK_COMPLETION)

    def test_request_had_survey_waffle_cookie(self):

        cases = [
            {"cookie": None, "expected": False},
            {"cookie": f"dwf_{WAFFLE_FLAG_TASK_COMPLETION}", "expected": True},
            {"cookie": f"dwf_something_else", "expected": False},
        ]
        for case in cases:
            with self.subTest(case=case):
                fake_request = RequestFactory().get("/")
                if case["cookie"] is not None:
                    fake_request.COOKIES[case["cookie"]] = True
                    # The value we set is not important in this test,
                    # just the presence of the cookie

                self.assertEqual(
                    request_had_survey_waffle_cookie(fake_request), case["expected"]
                )

    def test_waffle_flag_enabled_with_percentage_rule__happy_path(self):

        # Show it's set up with ONLY the percent rule in place
        self.assertEqual(self.flag.percent, 5.0)
        self.assertIsNone(self.flag.everyone)
        self.assertFalse(self.flag.languages)
        self.assertFalse(self.flag.authenticated)
        self.assertFalse(self.flag.staff)
        self.assertFalse(self.flag.superusers)

        self.assertTrue(
            waffle_flag_enabled_with_percentage_rule(
                request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
            )
        )

    def test_waffle_flag_enabled_with_percentage_rule__unhappy_path__flag_missing(self):

        self.flag.delete()

        self.assertFalse(
            waffle_flag_enabled_with_percentage_rule(
                request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
            )
        )

    def test_waffle_flag_enabled_with_percentage_rule__unhappy_path__zero_percent(self):
        # Zero percent is a way to disable the flag
        self.flag.percent = 0
        self.flag.save()

        self.assertEqual(self.flag.percent, 0.0)  #  only difference from test above
        self.assertIsNone(self.flag.everyone)
        self.assertFalse(self.flag.languages)
        self.assertFalse(self.flag.authenticated)
        self.assertFalse(self.flag.staff)
        self.assertFalse(self.flag.superusers)

        self.assertFalse(
            waffle_flag_enabled_with_percentage_rule(
                request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
            )
        )

    @mock.patch(
        "developerportal.apps.common.middleware.waffle.models.Flag._is_active_for_user"
    )
    def test_waffle_flag_enabled_with_percentage_rule__unhappy_paths__active_for_user(
        self, mock__is_active_for_user
    ):

        self.assertEqual(self.flag.percent, 5.0)
        mock__is_active_for_user.return_value = True

        self.assertFalse(
            waffle_flag_enabled_with_percentage_rule(
                request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
            )
        )

    @mock.patch(
        "developerportal.apps.common.middleware.waffle.models."
        "Flag._is_active_for_language"
    )
    def test_waffle_flag_enabled_with_percentage_rule__unhappy_path__active_for_lang(
        self, mock__is_active_for_language
    ):

        self.assertEqual(self.flag.percent, 5.0)
        mock__is_active_for_language.return_value = True

        self.assertFalse(
            waffle_flag_enabled_with_percentage_rule(
                request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
            )
        )

    def test_waffle_flag_enabled_with_percentage_rule__other_unhappy_paths(self):
        cases = [
            {"fieldname": "testing", "value": True},
            {"fieldname": "everyone", "value": False},
            {"fieldname": "everyone", "value": True},
        ]

        self.assertEqual(self.flag.percent, 5.0)
        for case in cases:
            with self.subTest(case=case):
                self.assertTrue(
                    waffle_flag_enabled_with_percentage_rule(
                        request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
                    )
                )
                orig_val = getattr(self.flag, case["fieldname"])
                setattr(self.flag, case["fieldname"], case["value"])
                self.flag.save()

                self.assertFalse(
                    waffle_flag_enabled_with_percentage_rule(
                        request=mock.Mock(), flag_name=WAFFLE_FLAG_TASK_COMPLETION
                    )
                )
                # restore original value for that field ready for next test
                setattr(self.flag, case["fieldname"], orig_val)
                self.flag.save()

    @mock.patch(
        "developerportal.apps.common.middleware."
        "waffle_flag_enabled_with_percentage_rule"
    )
    def test_flag_enabled_and_no_cookie_set_means_caching_skipped(
        self, mock_waffle_flag_enabled_with_percentage_rule
    ):
        mock_waffle_flag_enabled_with_percentage_rule.return_value = True
        mock_request = RequestFactory().get("/")
        assert not mock_request.COOKIES

        mock_response = HttpResponse("Test response")
        mock_get_response = mock.Mock(return_value=mock_response)

        middleware_func = survey_waffle_flag_cdn_middleware(mock_get_response)
        response = middleware_func(mock_request)

        assert response == mock_response
        self.assertEqual(response["no-cache"], "Set-Cookie")
        self.assertEqual(response["Cache-Control"], "no-cache")

    @mock.patch(
        "developerportal.apps.common.middleware."
        "waffle_flag_enabled_with_percentage_rule"
    )
    def test_flag_enabled_and_cookie_set_means_caching_not_skipped(
        self, mock_waffle_flag_enabled_with_percentage_rule
    ):
        mock_waffle_flag_enabled_with_percentage_rule.return_value = True
        mock_request = RequestFactory().get("/")
        mock_request.COOKIES[f"dwf_{WAFFLE_FLAG_TASK_COMPLETION}"] = True

        mock_response = HttpResponse("Test response")
        mock_get_response = mock.Mock(return_value=mock_response)

        middleware_func = survey_waffle_flag_cdn_middleware(mock_get_response)
        response = middleware_func(mock_request)

        assert response == mock_response
        self.assertFalse("no-cache" in response)
        self.assertFalse("Cache-Control" in response)

    @mock.patch(
        "developerportal.apps.common.middleware."
        "waffle_flag_enabled_with_percentage_rule"
    )
    def test_flag_absent_and_no_cookie_set_means_caching_not_skipped(
        self, mock_waffle_flag_enabled_with_percentage_rule
    ):
        mock_waffle_flag_enabled_with_percentage_rule.return_value = False
        mock_request = RequestFactory().get("/")
        assert not mock_request.COOKIES

        mock_response = HttpResponse("Test response")
        mock_get_response = mock.Mock(return_value=mock_response)

        middleware_func = survey_waffle_flag_cdn_middleware(mock_get_response)
        response = middleware_func(mock_request)

        assert response == mock_response
        self.assertFalse("no-cache" in response)
        self.assertFalse("Cache-Control" in response)

    @mock.patch(
        "developerportal.apps.common.middleware."
        "waffle_flag_enabled_with_percentage_rule"
    )
    def test_flag_absent_and_cookie_set_means_caching_not_skipped(
        self, mock_waffle_flag_enabled_with_percentage_rule
    ):
        mock_waffle_flag_enabled_with_percentage_rule.return_value = False
        mock_request = RequestFactory().get("/")
        mock_request.COOKIES[f"dwf_{WAFFLE_FLAG_TASK_COMPLETION}"] = True

        mock_response = HttpResponse("Test response")
        mock_get_response = mock.Mock(return_value=mock_response)

        middleware_func = survey_waffle_flag_cdn_middleware(mock_get_response)
        response = middleware_func(mock_request)

        assert response == mock_response
        self.assertFalse("no-cache" in response)
        self.assertFalse("Cache-Control" in response)
