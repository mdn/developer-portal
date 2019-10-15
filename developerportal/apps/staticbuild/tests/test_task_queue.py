import datetime
from unittest import mock

from django.test import TestCase, override_settings

import pytz
from developerportal.apps.staticbuild.wagtail_hooks import (
    _generate_build_path,
    _static_build_async,
)


class TaskQueueBuildTests(TestCase):
    @override_settings(BUILD_DIR="/path/to/build/dir/")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.tz_now")
    def test__generate_build_path(self, mock_tz_now):
        mock_tz_now.return_value = datetime.datetime(
            2001, 12, 25, 1, 23, 45, 123456, tzinfo=pytz.utc
        )
        self.assertEqual(
            _generate_build_path(),
            "/path/to/build/dir/2001-12-25T01:23:45.123456+00:00",
        )

    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.shutil.rmtree")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks._generate_build_path")
    def test_static_build_async__uses_specific_build_path(
        self, mock_generate_build_path, mock_rmtree, mock_call_command
    ):
        mock_generate_build_path.return_value = "/build/subdir/"

        _static_build_async()

        self.assertEqual(mock_call_command.call_count, 2)
        assert mock_call_command.call_args_list[0][0][0] == "build"
        assert mock_call_command.call_args_list[0][1]["build_dir"] == "/build/subdir/"

        assert mock_call_command.call_args_list[1][0][0] == "publish"
        assert mock_call_command.call_args_list[1][1]["build_dir"] == "/build/subdir/"

        mock_rmtree.assert_called_once_with("/build/subdir/")
