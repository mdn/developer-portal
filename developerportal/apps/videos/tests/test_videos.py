from wagtail.tests.utils import WagtailPageTests

from ...home.models import HomePage
from ..models import Video, Videos


class VideoTests(WagtailPageTests):
    """Tests for the Video model."""

    def test_video_parent_pages(self):
        self.assertAllowedParentPageTypes(Video, {Videos})

    def test_video_subpages(self):
        self.assertAllowedSubpageTypes(Video, {})


class VideosTests(WagtailPageTests):
    """Tests for the Videos model."""

    def test_videos_parent_pages(self):
        self.assertAllowedParentPageTypes(Videos, {HomePage})

    def test_videos_subpages(self):
        self.assertAllowedSubpageTypes(Videos, {Video})
