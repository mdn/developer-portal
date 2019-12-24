import datetime
from unittest import mock

from django.test import TestCase, override_settings

from developerportal.apps.taskqueue.utils import invalidate_cdn


@override_settings(AWS_CLOUDFRONT_DISTRIBUTION_ID="testdistribution")
class CDNInvalidationTests(TestCase):
    def setUp(self):
        self.mock_bucket = mock.Mock("fake-bucket")
        self.mock_cloudfront_client = mock.Mock(name="cloudfront_client")

        mock_create_invalidation = mock.Mock("create_invalidation")
        self.mock_cloudfront_client.create_invalidation.return_value = (
            mock_create_invalidation
        )

    @mock.patch("developerportal.apps.taskqueue.utils.boto3.client")
    @mock.patch("developerportal.apps.taskqueue.utils.tz_now")
    def test_invalidate_cdn(self, mock_tz_now, mock_client):

        invalidation_path_cases = [
            {"input": None, "expected": ["/*"]},
            {"input": ["/*"], "expected": ["/*"]},
            {"input": ["/foo/*"], "expected": ["/foo/*"]},
            {"input": ["/foo/bar/baz"], "expected": ["/foo/bar/baz"]},
        ]

        for case in invalidation_path_cases:
            with self.subTest(case=case):

                mock_client.return_value = self.mock_cloudfront_client

                self.mock_cloudfront_client.create_invalidation.reset_mock()

                _mock_tz_now_val = datetime.datetime(2019, 10, 9, 17, 4, 54, 745000)
                mock_tz_now.return_value = _mock_tz_now_val
                expected_caller_reference = _mock_tz_now_val.isoformat()

                _mock_response_content = {
                    "ResponseMetadata": {
                        "RequestId": "TEST-TEST-TEST-TEST-TESTTESTTEST",
                        "HTTPStatusCode": 201,
                        "HTTPHeaders": {
                            "x-amzn-requestid": "TEST-TEST-TEST-TEST-TESTTESTTEST",
                            "location": (
                                "https://cloudfront.amazonaws.com/2019-03-26/distribution/"  # noqa
                                "testdistribution/invalidation/INVALIDATION_ID"
                            ),
                            "content-type": "text/xml",
                            "content-length": "373",
                            "date": "Wed, 09 Oct 2019 17:04:54 GMT",
                        },
                        "RetryAttempts": 0,
                    },
                    "Location": (
                        "https://cloudfront.amazonaws.com/2019-03-26/distribution/"
                        "testdistribution/invalidation/INVALIDATION_ID"
                    ),
                    "Invalidation": {
                        "Id": "INVALIDATION_ID",
                        "Status": "InProgress",
                        "CreateTime": datetime.datetime(2019, 10, 9, 17, 4, 54, 745000),
                        "InvalidationBatch": {
                            "Paths": {"Quantity": 1, "Items": case["expected"]},
                            "CallerReference": expected_caller_reference,
                        },
                    },
                }
                self.mock_cloudfront_client.create_invalidation.return_value = (
                    _mock_response_content
                )

                with self.assertLogs(
                    "developerportal.apps.taskqueue.utils", level="DEBUG"
                ) as cm:
                    invalidate_cdn(invalidation_targets=case["input"])

                self.mock_cloudfront_client.create_invalidation.assert_called_once_with(
                    DistributionId="testdistribution",
                    InvalidationBatch={
                        "Paths": {"Items": case["expected"], "Quantity": 1},
                        "CallerReference": expected_caller_reference,
                    },
                )

                self.assertEqual(
                    cm.output,
                    [
                        (
                            "INFO:developerportal.apps.taskqueue.utils:"
                            "Purging Cloudfront distribtion ID testdistribution."
                        ),
                        (
                            "INFO:developerportal.apps.taskqueue.utils:"
                            "Got a positive response from Cloudfront. "
                            "Invalidation status: InProgress"
                        ),
                        (
                            "DEBUG:developerportal.apps.taskqueue.utils:Response: {}"
                        ).format(_mock_response_content),
                    ],
                )

    @mock.patch("developerportal.apps.taskqueue.utils.boto3.client")
    def test_invalidate_cdn__unhappy_path(self, mock_client):
        mock_client.return_value = self.mock_cloudfront_client

        _mock_response_content = {
            "ResponseMetadata": {
                "RequestId": "TEST-TEST-TEST-TEST-TESTTESTTEST",
                "HTTPStatusCode": 403,
                "HTTPHeaders": {
                    "x-amzn-requestid": "TEST-TEST-TEST-TEST-TESTTESTTEST",
                    "location": (
                        "https://cloudfront.amazonaws.com/2019-03-26/distribution/"
                        "testdistribution/invalidation/INVALIDATION_ID"
                    ),
                    "content-type": "text/xml",
                    "content-length": "373",
                    "date": "Wed, 09 Oct 2019 17:04:54 GMT",
                },
                "RetryAttempts": 0,
            },
            "Location": (
                "https://cloudfront.amazonaws.com/2019-03-26/distribution/"
                "testdistribution/invalidation/INVALIDATION_ID"
            ),
        }
        self.mock_cloudfront_client.create_invalidation.return_value = (
            _mock_response_content
        )

        with self.assertLogs(
            "developerportal.apps.taskqueue.utils", level="DEBUG"
        ) as cm:
            invalidate_cdn()

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.taskqueue.utils:"
                    "Purging Cloudfront distribtion ID testdistribution."
                ),
                (
                    "WARNING:developerportal.apps.taskqueue.utils:"
                    "Got an unexpected response from Cloudfront: {}"
                ).format(_mock_response_content),
            ],
        )
