import datetime
from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

import pytz

from developerportal.apps.staticbuild.context_managers import redis_lock
from developerportal.apps.staticbuild.wagtail_hooks import (
    EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME,
    SENTINEL_KEY_NAME,
    SENTINEL_LOCK_NAME,
    _generate_build_path,
    _get_build_needed_sentinel,
    _is_build_and_sync_job,
    _request_static_build,
    _set_build_needed_sentinel,
    _static_build_async,
    static_build,
)


class TaskQueueBuildTests(TestCase):
    def setUp(self):
        cache.delete(SENTINEL_KEY_NAME)
        cache.delete(SENTINEL_LOCK_NAME)

    def tearDown(self):
        cache.delete(SENTINEL_KEY_NAME)
        cache.delete(SENTINEL_LOCK_NAME)

    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.tz_now")
    def test__generate_build_path(self, mock_tz_now):
        mock_tz_now.return_value = datetime.datetime(
            2001, 12, 25, 1, 23, 45, 123456, tzinfo=pytz.utc
        )
        self.assertEqual(
            _generate_build_path(),
            f"{settings.BUILD_DIR}/2001-12-25T01:23:45.123456+00:00",
        )

    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.shutil.rmtree")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks._generate_build_path")
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._get_build_needed_sentinel"
    )
    def test__static_build_async(
        self,
        mock_get_build_needed_sentinel,
        mock_generate_build_path,
        mock_rmtree,
        mock_call_command,
    ):
        mock_get_build_needed_sentinel.return_value = True  # else the build is blocked
        mock_generate_build_path.return_value = "/build/subdir/"

        _static_build_async()

        self.assertEqual(mock_call_command.call_count, 2)
        assert mock_call_command.call_args_list[0][0][0] == "build"
        assert mock_call_command.call_args_list[0][1]["build_dir"] == "/build/subdir/"

        assert mock_call_command.call_args_list[1][0][0] == "publish"
        assert mock_call_command.call_args_list[1][1]["build_dir"] == "/build/subdir/"

        mock_rmtree.assert_called_once_with("/build/subdir/")

    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.shutil.rmtree")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks._generate_build_path")
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._get_build_needed_sentinel"
    )
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._set_build_needed_sentinel"
    )
    def test__static_build_async__not_requested(
        self,
        mock_set_build_needed_sentinel,
        mock_get_build_needed_sentinel,
        mock_generate_build_path,
        mock_rmtree,
        mock_call_command,
    ):
        mock_get_build_needed_sentinel.return_value = False

        with self.assertLogs(
            "developerportal.apps.staticbuild.wagtail_hooks", level="INFO"
        ) as cm:
            _static_build_async()

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.staticbuild.wagtail_hooks:"
                    "[Static-build-and-sync] No fresh static build requested."
                )
            ],
        )

        assert not mock_generate_build_path.called
        assert not mock_call_command.called
        assert not mock_rmtree.called
        assert not mock_set_build_needed_sentinel.called

    @mock.patch("developerportal.apps.staticbuild.context_managers.cache.add")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.call_command")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks.shutil.rmtree")
    @mock.patch("developerportal.apps.staticbuild.wagtail_hooks._generate_build_path")
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._get_build_needed_sentinel"
    )
    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._set_build_needed_sentinel"
    )
    def test__static_build_async__locked_but_requested(
        self,
        mock_set_build_needed_sentinel,
        mock_get_build_needed_sentinel,
        mock_generate_build_path,
        mock_rmtree,
        mock_call_command,
        mock_cache_add,
    ):
        mock_get_build_needed_sentinel.return_value = True  # else the build is blocked
        mock_generate_build_path.return_value = "/build/subdir/"

        mock_get_build_needed_sentinel.return_value = True  # else the build is blocked

        # Necause we're faking the sentinel's presence we can also check that it's
        # re-set by a lock-blocked _static_build_async()
        assert cache.get(SENTINEL_KEY_NAME) is None  #  for comparison later

        # Mimick the idea that the job couldn't get a lock because
        mock_cache_add.return_value = False

        assert not mock_set_build_needed_sentinel.called

        _static_build_async()

        assert not mock_generate_build_path.called
        assert not mock_call_command.called
        assert not mock_rmtree.called
        assert mock_cache_add.call_count == 1

        # The blocked job should have set a flag for a retry next CeleryBeat ping
        assert mock_set_build_needed_sentinel.call_count == 1

    def test__is_build_and_sync_job(self):
        for config in [
            {"name": "test", "expected_result": False},
            {"name": EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME, "expected_result": True},
        ]:
            with self.subTest(config=config):
                job_details = {"name": config["name"]}
                self.assertEqual(
                    _is_build_and_sync_job(job_details), config["expected_result"]
                )

    def test__set_build_needed_sentinel(self):
        assert cache.get(SENTINEL_KEY_NAME) is None
        _set_build_needed_sentinel(oid="test")
        assert cache.get(SENTINEL_KEY_NAME) is True

    def test__get_build_needed_sentinel(self):
        assert cache.get(SENTINEL_KEY_NAME) is None
        assert _get_build_needed_sentinel(oid="test") is None
        cache.set(SENTINEL_KEY_NAME, True)
        assert _get_build_needed_sentinel(oid="test") is True

    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._set_build_needed_sentinel"
    )
    def test__request_static_build(self, mock_set_build_needed_sentinel):
        assert not mock_set_build_needed_sentinel.called
        _request_static_build()
        assert mock_set_build_needed_sentinel.call_count == 1

    @mock.patch(
        "developerportal.apps.staticbuild.wagtail_hooks._request_static_build.delay"
    )
    def test_static_build(self, mock_request_static_build_delay):
        assert not mock_request_static_build_delay.called
        static_build()
        assert mock_request_static_build_delay.call_count == 1


class ContextManagerTests(TestCase):
    def test_redis_lock(self):

        #  locking while also locked is not allowed
        with redis_lock("test-lock-id", "oid-1") as acquired_1:
            assert acquired_1 is True

            # Can't re-lock a locked lock
            with redis_lock("test-lock-id", "oid-2") as acquired_2:
                assert acquired_2 is None

            # Can lock an unlocked lock inside another lock (sheesh!)
            with redis_lock("alternative-test-lock-id", "oid-2") as acquired_3:
                assert acquired_3 is True

        # Can re-lock a released lock
        with redis_lock("test-lock-id", "oid-3") as acquired_4:
            assert acquired_4 is True

        # Can re-lock previously denied lock (same oid) when it's been released
        with redis_lock("test-lock-id", "oid-2a") as acquired_5:
            assert acquired_5 is True
