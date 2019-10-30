from wagtail.core.models import Page

from developerportal.apps.common.test_helpers import PatchedWagtailPageTests

from ..models import ExternalArticle, ExternalEvent, ExternalVideo


class ExternalArticleTests(PatchedWagtailPageTests):
    """Tests for the ExternalArticle model."""

    def test_external_article_parent_pages(self):
        self.assertAllowedParentPageTypes(ExternalArticle, {Page})

    def test_external_article_subpages(self):
        self.assertAllowedSubpageTypes(ExternalArticle, {})


class ExternalEventTests(PatchedWagtailPageTests):
    """Tests for the ExternalEvent model."""

    def test_external_event_parent_pages(self):
        self.assertAllowedParentPageTypes(ExternalEvent, {Page})

    def test_external_event_subpages(self):
        self.assertAllowedSubpageTypes(ExternalEvent, {})


class ExternalVideoTests(PatchedWagtailPageTests):
    """Tests for the ExternalVideo model."""

    def test_external_video_parent_pages(self):
        self.assertAllowedParentPageTypes(ExternalVideo, {Page})

    def test_external_video_subpages(self):
        self.assertAllowedSubpageTypes(ExternalVideo, {})
