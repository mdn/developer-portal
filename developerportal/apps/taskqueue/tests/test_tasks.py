from unittest import mock

from django.test import TestCase

from ..tasks import (
    _warm_cdn,
    invalidate_entire_cdn,
    selectively_invalidate_cdn,
    selectively_warm_cdn,
    warm_entire_cdn,
)


class TasksTestCase(TestCase):
    fixtures = ["common.json"]

    @mock.patch("developerportal.apps.taskqueue.tasks.invalidate_cdn")
    @mock.patch("developerportal.apps.taskqueue.tasks.warm_entire_cdn.apply_async")
    def test_invalidate_entire_cdn(
        self, mock_warm_entire_cdn_apply_async, mock_invalidate_cdn
    ):
        assert not mock_invalidate_cdn.called
        invalidate_entire_cdn()
        mock_invalidate_cdn.assert_called_once_with()

        mock_warm_entire_cdn_apply_async.assert_called_once_with(countdown=60 * 15)

    @mock.patch("developerportal.apps.taskqueue.tasks.invalidate_cdn")
    @mock.patch("developerportal.apps.taskqueue.tasks.selectively_warm_cdn.apply_async")
    def test_selectively_invalidate_cdn(
        self, mock_selectively_warm_cdn_apply_async, mock_invalidate_cdn
    ):

        assert not mock_invalidate_cdn.called
        selectively_invalidate_cdn()
        mock_invalidate_cdn.assert_called_once_with(
            invalidation_targets=["/events/*", "/communities/people/*", "/topics/*"]
        )
        host = "http://developer-portal-127-0-0-1.nip.io"

        urls = [f"{host}/events/", f"{host}/communities/people/", f"{host}/topics/"]
        mock_selectively_warm_cdn_apply_async.assert_called_once_with(
            args=[urls], countdown=60 * 15
        )

    @mock.patch("developerportal.apps.taskqueue.tasks.get_all_urls_from_sitemap")
    @mock.patch("developerportal.apps.taskqueue.tasks._warm_cdn")
    def test_warm_entire_cdn(self, mock_warm_cdn, mock_get_all_urls_from_sitemap):

        _urls = ["/foo/", "/bar/", "/baz/bam"]

        mock_get_all_urls_from_sitemap.return_value = _urls

        warm_entire_cdn()
        mock_get_all_urls_from_sitemap.assert_called_once_with()
        mock_warm_cdn.assert_called_once_with(_urls)

    @mock.patch("developerportal.apps.taskqueue.tasks._warm_cdn")
    def test_selectively_warm_cdn(self, mock_warm_cdn):

        _urls = ["/foo/", "/bar/", "/baz/bam"]

        selectively_warm_cdn(_urls)
        mock_warm_cdn.assert_called_once_with(_urls)

    @mock.patch("developerportal.apps.taskqueue.tasks.requests.get")
    def test__warm_cdn__happy_path(self, mock_requests_get):

        mock_response = mock.Mock(name="mock_response")
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        with self.assertLogs(
            "developerportal.apps.taskqueue.tasks", level="INFO"
        ) as cm:
            _urls = ["/foo/", "/bar/", "/baz/bam"]
            _warm_cdn(_urls)
            assert mock_requests_get.call_count == 3
            assert [x[0][0] for x in mock_requests_get.call_args_list] == _urls

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.taskqueue.tasks:"
                    "Warming CDN. 3 URLs obtained from sitemap."
                ),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Requesting 1/3: /foo/"),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Requesting 2/3: /bar/"),
                (
                    "INFO:developerportal.apps.taskqueue.tasks:"
                    "Requesting 3/3: /baz/bam"
                ),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Warming complete."),
            ],
        )

    @mock.patch("developerportal.apps.taskqueue.tasks.requests.get")
    def test__warm_cdn__unhappy_path(self, mock_requests_get):
        with self.assertLogs(
            "developerportal.apps.taskqueue.tasks", level="INFO"
        ) as cm:

            mock_response = mock.Mock(name="mock_response")
            mock_response.status_code = 404
            mock_requests_get.return_value = mock_response

            _urls = ["/foo/", "/bar/", "/baz/bam"]
            _warm_cdn(_urls)
            assert mock_requests_get.call_count == 3
            assert [x[0][0] for x in mock_requests_get.call_args_list] == _urls

        empty_exception_traceback_string = "\nNoneType: None"

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.taskqueue.tasks:"
                    "Warming CDN. 3 URLs obtained from sitemap."
                ),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Requesting 1/3: /foo/"),
                (
                    "ERROR:developerportal.apps.taskqueue.tasks:"
                    f"Failed to get /foo/ {empty_exception_traceback_string}"
                ),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Requesting 2/3: /bar/"),
                (
                    "ERROR:developerportal.apps.taskqueue.tasks:"
                    f"Failed to get /bar/ {empty_exception_traceback_string}"
                ),
                (
                    "INFO:developerportal.apps.taskqueue.tasks:"
                    "Requesting 3/3: /baz/bam"
                ),
                (
                    "ERROR:developerportal.apps.taskqueue.tasks:"
                    f"Failed to get /baz/bam {empty_exception_traceback_string}"
                ),
                ("INFO:developerportal.apps.taskqueue.tasks:" "Warming complete."),
            ],
        )
