import datetime
from unittest import mock

from django.test import TestCase

import pytz
from dateutil.tz import tzlocal

from ...mozimages.models import MozImage
from ..models import (
    ExternalArticle,
    ExternalContent,
    ExternalContentPageManagerBase,
    ExternalEvent,
    ExternalVideo,
)
from .data.test_images_as_bytearrays import image_one as image_one_bytearray


class ExternalContentPageManagerBaseTests(TestCase):
    def test_generate_draft_from_external_data__raises_NotImplementedError(self):
        with self.assertRaises(NotImplementedError):
            ExternalContent.objects.generate_draft_from_external_data(data={})

    @mock.patch("developerportal.apps.externalcontent.models." "requests.get")
    def test__store_external_image(self, mock_requests_get):

        mock_response = mock.Mock()
        mock_response.content = image_one_bytearray
        mock_requests_get.return_value = mock_response

        saved_image = ExternalContentPageManagerBase()._store_external_image(
            image_url="https://example.com/test.png"
        )

        mock_requests_get.assert_called_once_with("https://example.com/test.png")

        saved_image.file.seek(0)
        comparison_content = saved_image.file.read()
        self.assertEqual(bytearray(comparison_content), image_one_bytearray)


class ExternalArticlePageManagerTests(TestCase):
    @mock.patch(
        "developerportal.apps.externalcontent.models."
        "ExternalArticle.objects._store_external_image"
    )
    def test_generate_draft_from_external_data(self, mock_store_external_image):

        image = MozImage(width=1, height=1)
        image.save()
        mock_store_external_image.return_value = image

        data = dict(
            title="ECSY Developer tools extension",
            authors=["Fernando Serrano"],  # not used for now
            url="https://blog.mozvr.com/ecsy-developer-tools/",
            image_url="https://blog.mozvr.com/content/images/2019/12/ecsy-header.png",
            timestamp=datetime.datetime(2019, 12, 10, 22, 47, 43, tzinfo=pytz.UTC),
        )

        obj = ExternalArticle.objects.generate_draft_from_external_data(data)
        self.assertEqual(type(obj), ExternalArticle)
        self.assertEqual(
            obj.slug,
            "c0a61483f56d003695c55eb33a8da04a5f32cfd2"
            # hashlib.sha1(str(data).encode('utf-8')).hexdigest()
        )
        self.assertEqual(obj.title, data["title"])
        self.assertEqual(obj.draft_title, data["title"])
        self.assertEqual(obj.external_url, data["url"])
        self.assertEqual(obj.date, data["timestamp"].date())
        mock_store_external_image.assert_called_once_with(data["image_url"])
        self.assertEqual(obj.image, image)


class ExternalVideoPageManagerTests(TestCase):
    @mock.patch(
        "developerportal.apps.externalcontent.models."
        "ExternalVideo.objects._store_external_image"
    )
    def test_generate_draft_from_external_data(self, mock_store_external_image):
        image = MozImage(width=1, height=1)
        image.save()
        mock_store_external_image.return_value = image

        data = dict(
            title="Where do Browser Styles Come From?",
            authors=["Mozilla Developer"],  # Not used for now
            url="https://www.youtube.com/watch?v=spK_S0HfzFw",
            image_url="https://i4.ytimg.com/vi/spK_S0HfzFw/hqdefault.jpg",
            timestamp=datetime.datetime(2019, 12, 11, 11, 0, 10, tzinfo=tzlocal()),
        )

        obj = ExternalVideo.objects.generate_draft_from_external_data(data)
        self.assertEqual(type(obj), ExternalVideo)
        self.assertEqual(
            obj.slug,
            "a36dd198ae6c88fbec737f799dfe640d0f9ded90",
            # hashlib.sha1(str(data).encode('utf-8')).hexdigest()
        )
        self.assertEqual(obj.title, data["title"])
        self.assertEqual(obj.draft_title, data["title"])
        self.assertEqual(obj.external_url, data["url"])
        self.assertEqual(obj.date, data["timestamp"].date())
        mock_store_external_image.assert_called_once_with(data["image_url"])
        self.assertEqual(obj.image, image)


class ExternalEventPageManagerTests(TestCase):
    def test_generate_draft_from_external_data__raises_NotImplementedError(self):
        with self.assertRaises(NotImplementedError):
            ExternalEvent.objects.generate_draft_from_external_data(data={})
