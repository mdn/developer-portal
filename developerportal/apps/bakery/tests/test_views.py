# Tests for the custom views that we feed to wagtail-bakery

import datetime
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, Site

from developerportal.apps.bakery.views import (
    CloudfrontInvalidationView,
    S3RedirectManagementView,
    SitemapBuildableView,
    is_secure_request,
)


class S3RedirectManagementViewTest(TestCase):
    def setUp(self):
        self.view = S3RedirectManagementView()
        self.homepage = Page.objects.last()
        Site.objects.all().delete()
        self.site = Site.objects.create(
            hostname="test", is_default_site=True, root_page=self.homepage
        )

    @mock.patch("developerportal.apps.bakery.views.get_s3_client")
    def test_post_publish(self, mock_get_s3_client):

        mock_bucket = mock.Mock("fake-bucket")
        # Sort out a `name` attribute for the mock S3 Bucket
        mocked_name = mock.PropertyMock(return_value="devportal_fake")
        type(mock_bucket).name = mocked_name

        mock_client = mock.Mock("fake-client")
        mock_put_object = mock.Mock("put_object()")
        mock_client.put_object = mock_put_object

        mock_resource = mock.Mock("fake-resource")

        mock_get_s3_client.return_value = (mock_client, mock_resource)

        # redirect_to_new_path
        Redirect.objects.create(
            old_path="/old_path/here/",
            redirect_page=self.homepage,  # contrived example, but valid
            site=self.site,  #  ie, it's only for the default site
        )

        # redirect_to_separate_url
        Redirect.objects.create(
            old_path="/something",
            redirect_link="https://example.com/test/",
            site=None,  # ie, it's a pan-Wagtail redirect
        )

        with self.assertLogs("developerportal.apps.bakery.views", level="INFO") as cm:
            self.view.post_publish(mock_bucket)

        assert mock_put_object.call_count == 2

        assert mock_put_object.call_args_list[0][1] == {
            "ACL": "public-read",
            "Bucket": "devportal_fake",
            "Key": "old_path/here/",
            "WebsiteRedirectLocation": "/",
        }

        assert mock_put_object.call_args_list[1][1] == {
            "ACL": "public-read",
            "Bucket": "devportal_fake",
            "Key": "something",
            "WebsiteRedirectLocation": "https://example.com/test/",
        }

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.bakery.views:Adding S3 Website "
                    "Redirect in devportal_fake from old_path/here/ to /"
                ),
                (
                    "INFO:developerportal.apps.bakery.views:Adding S3 Website "
                    "Redirect in devportal_fake from something to "
                    "https://example.com/test/"
                ),
            ],
        )

    @mock.patch("developerportal.apps.bakery.views.get_s3_client")
    def test_post_publish__no_redirects_exist(self, mock_get_s3_client):

        mock_bucket = mock.Mock("fake-bucket")
        mock_client = mock.Mock("fake-client")
        mock_put_object = mock.Mock("put_object()")
        mock_client.put_object = mock_put_object
        mock_resource = mock.Mock("fake-resource")

        mock_get_s3_client.return_value = (mock_client, mock_resource)

        # redirect_to_new_path
        assert not Redirect.objects.exists()

        with self.assertLogs("developerportal.apps.bakery.views", level="INFO") as cm:
            self.view.post_publish(mock_bucket)

        assert mock_put_object.call_count == 0

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.bakery.views:No Wagtail Redirects "
                    "detected, so no S3 Website Redirects to create"
                )
            ],
        )


@override_settings(AWS_CLOUDFRONT_DISTRIBUTION_ID="testdistribution")
class CloudfrontInvalidationViewTests(TestCase):
    def setUp(self):
        self.view = CloudfrontInvalidationView()

        self.mock_bucket = mock.Mock("fake-bucket")
        self.mock_cloudfront_client = mock.Mock(name="cloudfront_client")

        mock_create_invalidation = mock.Mock("create_invalidation")
        self.mock_cloudfront_client.create_invalidation.return_value = (
            mock_create_invalidation
        )

    @mock.patch("developerportal.apps.bakery.views.boto3.client")
    @mock.patch("developerportal.apps.bakery.views.tz_now")
    def test_post_publish(self, mock_tz_now, mock_client):

        mock_client.return_value = self.mock_cloudfront_client

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
            "Invalidation": {
                "Id": "INVALIDATION_ID",
                "Status": "InProgress",
                "CreateTime": datetime.datetime(2019, 10, 9, 17, 4, 54, 745000),
                "InvalidationBatch": {
                    "Paths": {"Quantity": 1, "Items": ["/*"]},
                    "CallerReference": expected_caller_reference,
                },
            },
        }
        self.mock_cloudfront_client.create_invalidation.return_value = (
            _mock_response_content
        )

        with self.assertLogs("developerportal.apps.bakery.views", level="DEBUG") as cm:
            self.view.post_publish(self.mock_bucket)

        self.mock_cloudfront_client.create_invalidation.assert_called_once_with(
            DistributionId="testdistribution",
            InvalidationBatch={
                "Paths": {"Items": ["/*"], "Quantity": 1},
                "CallerReference": expected_caller_reference,
            },
        )

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.bakery.views:"
                    "Purging Cloudfront distribtion ID testdistribution."
                ),
                (
                    "INFO:developerportal.apps.bakery.views:"
                    "Got a positive response from Cloudfront. "
                    "Invalidation status: InProgress"
                ),
                ("DEBUG:developerportal.apps.bakery.views:Response: {}").format(
                    _mock_response_content
                ),
            ],
        )

    @mock.patch("developerportal.apps.bakery.views.boto3.client")
    def test_post_publish__unhappy_path(self, mock_client):
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

        with self.assertLogs("developerportal.apps.bakery.views", level="DEBUG") as cm:
            self.view.post_publish(self.mock_bucket)

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.bakery.views:"
                    "Purging Cloudfront distribtion ID testdistribution."
                ),
                (
                    "WARNING:developerportal.apps.bakery.views:"
                    "Got an unexpected response from Cloudfront: {}"
                ).format(_mock_response_content),
            ],
        )

    @override_settings(AWS_CLOUDFRONT_DISTRIBUTION_ID=None)
    @mock.patch("developerportal.apps.bakery.views.boto3.client")
    def test_post_publish__no_config_set(self, mock_client):

        assert not mock_client.called

        with self.assertLogs("developerportal.apps.bakery.views", level="DEBUG") as cm:
            self.view.post_publish(self.mock_bucket)

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.bakery.views:"
                    "No Cloudfront distribtion ID configured. Skipping CDN purge."
                )
            ],
        )


class SitemapViewTests(TestCase):
    @mock.patch("developerportal.apps.bakery.views.SitemapBuildableView.get_content")
    @mock.patch("developerportal.apps.bakery.views.SitemapBuildableView.prep_directory")
    @mock.patch("developerportal.apps.bakery.views.SitemapBuildableView.build_file")
    def test_sitemap_generation(
        self, mock_build_file, mock_prep_directory, mock_get_content
    ):
        mock_get_content.return_value = "sitemap content here"

        with self.assertLogs("developerportal.apps.bakery.views", level="INFO") as cm:
            SitemapBuildableView().build_method()
        assert mock_prep_directory.call_count == 1
        assert mock_build_file.call_count == 1
        mock_build_file.assert_called_once_with(
            "/app/build/sitemap.xml", "sitemap content here"
        )
        self.assertEqual(
            cm.output,
            [
                "INFO:developerportal.apps.bakery.views:Building out XML sitemap.",
                "INFO:developerportal.apps.bakery.views:Sitemap building complete.",
            ],
        )


class HelpersTests(TestCase):
    def test_is_secure_request(self):
        site = Site.objects.first()

        port_params = [(80, False), (443, True), (8000, False)]
        for params in port_params:
            with self.subTest(params=params):
                site.port, expected_result = params
                self.assertEqual(is_secure_request(site), expected_result)

        settings_params = [(True, True), (False, False)]
        site.port = 80
        for params in settings_params:
            with self.subTest(params=params):
                secure_redirect, expected_result = params
                with override_settings(SECURE_SSL_REDIRECT=secure_redirect):
                    self.assertEqual(is_secure_request(site), expected_result)


class TestPipelineContents(TestCase):
    def test_build_pipeline_contains_all_required_views(self):
        # Light regression check - ensure all present and in right order
        self.assertEqual(
            settings.BAKERY_VIEWS,
            (
                (
                    "developerportal.apps.bakery.views."
                    "AllPublishedPagesViewAllowingSecureRedirect"
                ),
                "bakery.views.Buildable404View",
                "developerportal.apps.bakery.views.SitemapBuildableView",
                "developerportal.apps.bakery.views.S3RedirectManagementView",
                "developerportal.apps.bakery.views.CloudfrontInvalidationView",
            ),
        )
