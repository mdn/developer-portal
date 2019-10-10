# Tests for the custom views that we feed to wagtail-bakery

from unittest import mock

from django.test import TestCase

from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, Site

from developerportal.apps.bakery.views import S3RedirectManagementView


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
