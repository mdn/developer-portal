from unittest import mock

from django.test import TestCase

from developerportal.apps.home.models import HomePage


class TestAutomaticBakingUponPublish(TestCase):
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._request_static_build.delay"
    )
    def test_page_publish_triggers_async_tasks(self, mock_request_static_build_delay):
        self.homepage = HomePage.objects.get()

        assert not mock_request_static_build_delay.called

        # One doesn't publish a page, one publishes a Revision
        revision = self.homepage.save_revision()
        revision.publish()
        assert mock_request_static_build_delay.call_count == 1

    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._request_static_build.delay"
    )
    def test_page_unpublish_triggers_async_tasks(self, mock_request_static_build_delay):
        self.homepage = HomePage.objects.get()
        assert not mock_request_static_build_delay.called

        # One can direcly unpublish a page, without needing a revision
        self.homepage.unpublish()
        assert mock_request_static_build_delay.call_count == 1
