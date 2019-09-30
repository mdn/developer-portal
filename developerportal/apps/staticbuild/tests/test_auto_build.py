from unittest import mock

from django.test import TestCase, override_settings

from developerportal.apps.home.models import HomePage


@override_settings(CELERY_ALWAYS_EAGER=True)
class TestAutomaticBakingUponPublish(TestCase):
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    def test_page_publish_triggers_async_tasks(self, mock_call_command):
        self.homepage = HomePage.objects.get()

        mock_call_command.reset_mock()

        # One doesn't publish a page, one publishes a Revision
        revision = self.homepage.save_revision()
        revision.publish()

        assert mock_call_command.call_count == 2

        #  check for the call that builds the static site
        assert mock_call_command.call_args_list[0][0][0] == "build"

        # now check for the call to sync the static site to S3
        assert mock_call_command.call_args_list[1][0][0] == "publish"

    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    def test_page_unpublish_triggers_async_tasks(self, mock_call_command):
        self.homepage = HomePage.objects.get()
        mock_call_command.reset_mock()

        # One can direcly unpublish a page, without needing a revision
        self.homepage.unpublish()
        assert mock_call_command.call_count == 2

        #  check for the call that builds the static site
        assert mock_call_command.call_args_list[0][0][0] == "build"

        # now check for the call to sync the static site to S3
        assert mock_call_command.call_args_list[1][0][0] == "publish"
