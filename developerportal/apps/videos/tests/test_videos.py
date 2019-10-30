from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ...home.models import HomePage
from ..models import Video, Videos


class VideoTests(PatchedWagtailPageTests):
    """Tests for the Video model."""

    def test_video_parent_pages(self):
        self.assertAllowedParentPageTypes(Video, {Videos})

    def test_video_subpages(self):
        self.assertAllowedSubpageTypes(Video, {})


class VideosTests(PatchedWagtailPageTests):
    """Tests for the Videos model."""

    def test_videos_parent_pages(self):
        self.assertAllowedParentPageTypes(Videos, {HomePage})

    def test_videos_subpages(self):
        self.assertAllowedSubpageTypes(Videos, {Video})
