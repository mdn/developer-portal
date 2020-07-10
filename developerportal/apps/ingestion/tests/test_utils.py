import datetime
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

import pytz
from dateutil.tz import tzlocal

from developerportal.apps.ingestion.utils import (
    _get_item_description,
    _get_slug,
    fetch_external_data,
    ingest_content,
)

from ...articles.models import Article
from ...externalcontent.models import (
    ExternalArticle,
    ExternalContent,
    ExternalEvent,
    ExternalVideo,
)
from ...mozimages.models import MozImage
from ...videos.models import Video
from ..constants import INGESTION_USER_USERNAME
from ..models import IngestionConfiguration
from ..utils import (
    _get_factory_func,
    _make_external_article_page,
    _make_video_page,
    _store_external_image,
    generate_draft_from_external_data,
)
from .data.test_images_as_bytearrays import image_one as image_one_bytearray


@override_settings(AUTOMATICALLY_INGEST_CONTENT=True)
class UtilsTestCaseWithoutFixtures(TestCase):

    YOUTUBE_FEED_URL = (
        "file:///app/developerportal/apps/ingestion/tests/test_data/youtube_feed.xml"
    )
    BLOG_RSS_FEED_URL = (
        "file:///app/developerportal/apps/"
        "ingestion/tests/test_data/blog.mozvr.com_rss.xml"
    )

    def test_fetch_external_data__filters_to_only_new__rss(self):

        last_synced_from_dec_2019 = datetime.datetime(2019, 12, 1, tzinfo=pytz.UTC)
        last_synced_from_aug_2019 = datetime.datetime(2019, 8, 1, tzinfo=pytz.UTC)

        blog_data_post_dec = fetch_external_data(
            feed_url=self.BLOG_RSS_FEED_URL, last_synced=last_synced_from_dec_2019
        )
        self.assertEqual(len(blog_data_post_dec), 6)

        blog_data_post_aug = fetch_external_data(
            feed_url=self.BLOG_RSS_FEED_URL, last_synced=last_synced_from_aug_2019
        )
        self.assertEqual(len(blog_data_post_aug), 15)

        for i in range(6):
            self.assertEqual(blog_data_post_dec[i], blog_data_post_aug[i])

    def test_fetch_external_data__filters_to_only_new__atom(self):

        last_synced_from_dec_2019 = datetime.datetime(2019, 12, 1, tzinfo=pytz.UTC)
        last_synced_from_aug_2019 = datetime.datetime(2019, 8, 1, tzinfo=pytz.UTC)

        yt_data_post_dec = fetch_external_data(
            feed_url=self.YOUTUBE_FEED_URL, last_synced=last_synced_from_dec_2019
        )
        self.assertEqual(len(yt_data_post_dec), 6)

        yt_data_post_aug = fetch_external_data(
            feed_url=self.YOUTUBE_FEED_URL, last_synced=last_synced_from_aug_2019
        )
        self.assertEqual(len(yt_data_post_aug), 15)

        for i in range(6):
            self.assertEqual(yt_data_post_dec[i], yt_data_post_aug[i])

    def test_fetch_external_data__nothing_new_since_last_sync(self):
        last_synced_from_jan_2020 = datetime.datetime(2020, 1, 1, tzinfo=pytz.UTC)
        blog_data_post_jan = fetch_external_data(
            feed_url=self.YOUTUBE_FEED_URL, last_synced=last_synced_from_jan_2020
        )
        self.assertEqual(len(blog_data_post_jan), 0)

    def test_fetch_external_data__data_dict_contents__rss(self):

        last_synced_from_dec_2019 = datetime.datetime(2019, 12, 1, tzinfo=pytz.UTC)

        blog_data_post_dec = fetch_external_data(
            feed_url=self.BLOG_RSS_FEED_URL, last_synced=last_synced_from_dec_2019
        )
        expected = dict(
            title="ECSY Developer tools extension",
            authors=["Fernando Serrano"],
            url="https://blog.mozvr.com/ecsy-developer-tools/",
            description=(
                "<p>Two months ago we released ECSY, a framework-agnostic Entity "
                "Component System library you could use to build real time "
                "applications with the engine of your choice.</p>"
            ),
            image_url="https://blog.mozvr.com/content/images/2019/12/ecsy-header.png",
            timestamp=datetime.datetime(2019, 12, 10, 22, 47, 43, tzinfo=pytz.UTC),
        )
        self.assertEqual(blog_data_post_dec[5], expected)

    def test_fetch_external_data__data_dict_contents__atom(self):

        last_synced_from_jan_2019 = datetime.datetime(2019, 1, 1, tzinfo=pytz.UTC)

        yt_data_post_jan = fetch_external_data(
            feed_url=self.YOUTUBE_FEED_URL, last_synced=last_synced_from_jan_2019
        )
        expected = dict(
            title="Where do Browser Styles Come From?",
            authors=["Mozilla Developer"],
            url="https://www.youtube.com/watch?v=spK_S0HfzFw",
            description=(
                "<p>Not sure where that default 8px of margin on the body "
                "comes from? Here's how to find out!</p>"
            ),
            image_url="https://i4.ytimg.com/vi/spK_S0HfzFw/hqdefault.jpg",
            timestamp=datetime.datetime(2019, 12, 11, 11, 0, 10, tzinfo=tzlocal()),
        )
        self.assertEqual(yt_data_post_jan[2], expected)

    def test_fetch_external_data__unhappy_path_bad_feed(self):
        last_synced_from_jan_2019 = datetime.datetime(2019, 1, 1, tzinfo=pytz.UTC)

        bad_data = fetch_external_data(
            feed_url="file://example.com/fictional.feed.xml",
            last_synced=last_synced_from_jan_2019,
        )

        self.assertEqual(bad_data, [])


@override_settings(AUTOMATICALLY_INGEST_CONTENT=True)
class UtilsTestCaseWithFixtures(TestCase):

    fixtures = ["common.json"]

    @mock.patch("developerportal.apps.ingestion.utils.send_notification")
    @mock.patch("developerportal.apps.ingestion.utils.fetch_external_data")
    @mock.patch("developerportal.apps.ingestion.utils.tz_now")
    def test_ingest_content(
        self, mock_tz_now, mock_fetch_external_data, mock_send_notification
    ):

        _now = datetime.datetime(12, 12, 13, 12, 34, 56, tzinfo=pytz.UTC)
        mock_tz_now.return_value = _now

        ingestion_dummy_user = User.objects.get(username=INGESTION_USER_USERNAME)

        # Wipe any configs added via data migration 0002
        IngestionConfiguration.objects.all().delete()

        IngestionConfiguration.objects.create(
            source_name="One",
            source_url="https://example.com/one.xml",
            integration_type=IngestionConfiguration.CONTENT_TYPE_VIDEO,
            last_sync=datetime.datetime(12, 12, 12, tzinfo=pytz.UTC),
        )
        IngestionConfiguration.objects.create(
            source_name="Two",
            source_url="https://example.com/two.rss",
            integration_type=IngestionConfiguration.CONTENT_TYPE_ARTICLE,
            last_sync=datetime.datetime(12, 12, 12, tzinfo=pytz.UTC),
        )

        assert IngestionConfiguration.objects.filter(last_sync=_now).count() == 0

        video_return_value = [
            dict(
                title="Test one",
                authors=["Fernando McTest"],
                url="https://example.com/thing/one/",
                description="<p>Test description one</p>",
                # image_url="https://example.com/one.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
            dict(
                title="Test two",
                authors=["Alice McTest"],
                url="https://example.com/thing/two/",
                description="<p>Test description two</p>",
                # image_url="https://example.com/two.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
            dict(
                title="Test three",
                authors=["Mary McTest"],
                url="https://example.com/thing/three/",
                description="<p>Test description three</p>",
                # image_url="https://example.com/three.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
        ]

        mock_fetch_external_data.return_value = video_return_value

        # First try Video content
        assert Video.objects.count() == 0
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)
        assert Video.objects.count() == 3

        assert (
            Video.objects.filter(
                title="Test one", description="<p>Test description one</p>"
            ).count()
            == 1
        )
        assert (
            Video.objects.filter(
                title="Test two", description="<p>Test description two</p>"
            ).count()
            == 1
        )
        assert (
            Video.objects.filter(
                title="Test three", description="<p>Test description three</p>"
            ).count()
            == 1
        )

        # None of these has been published yet
        assert Video.objects.filter(first_published_at__isnull=True).count() == 3

        # Show the owner has been set
        assert Video.objects.filter(owner=ingestion_dummy_user).count() == 3

        assert mock_send_notification.call_count == 3

        article_return_value = video_return_value + [
            dict(
                title="Test four",
                authors=["Barry McTest"],
                url="https://example.com/thing/four/",
                description="<p>Test description four</p>",
                # image_url="https://example.com/four.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            )
        ]
        for x in article_return_value:
            x["title"] += " for Post"

        mock_send_notification.reset_mock()
        mock_fetch_external_data.reset_mock()
        mock_fetch_external_data.return_value = article_return_value

        # Now try Article content
        assert ExternalArticle.objects.count() == 0
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_ARTICLE)
        assert ExternalArticle.objects.count() == 4

        assert (
            ExternalArticle.objects.filter(
                title="Test one for Post", description="<p>Test description one</p>"
            ).count()
            == 1
        )
        assert (
            ExternalArticle.objects.filter(
                title="Test two for Post", description="<p>Test description two</p>"
            ).count()
            == 1
        )
        assert (
            ExternalArticle.objects.filter(
                title="Test three for Post", description="<p>Test description three</p>"
            ).count()
            == 1
        )
        assert (
            ExternalArticle.objects.filter(
                title="Test four for Post", description="<p>Test description four</p>"
            ).count()
            == 1
        )

        # None of these has been published yet
        assert (
            ExternalArticle.objects.filter(first_published_at__isnull=True).count() == 4
        )
        # Show the owner has been set
        assert ExternalArticle.objects.filter(owner=ingestion_dummy_user).count() == 4

        assert IngestionConfiguration.objects.filter(last_sync=_now).count() == 2

        assert mock_send_notification.call_count == 4

    @override_settings(NOTIFY_AFTER_INGESTING_CONTENT=False)
    @mock.patch("developerportal.apps.ingestion.utils.send_notification")
    @mock.patch("developerportal.apps.ingestion.utils.fetch_external_data")
    @mock.patch("developerportal.apps.ingestion.utils.tz_now")
    def test_ingest_content__no_notifications_option_set(
        self, mock_tz_now, mock_fetch_external_data, mock_send_notification
    ):

        _now = datetime.datetime(12, 12, 13, 12, 34, 56, tzinfo=pytz.UTC)
        mock_tz_now.return_value = _now

        # Wipe any configs added via data migration 0002
        IngestionConfiguration.objects.all().delete()

        IngestionConfiguration.objects.create(
            source_name="One",
            source_url="https://example.com/one.xml",
            integration_type=IngestionConfiguration.CONTENT_TYPE_VIDEO,
            last_sync=datetime.datetime(12, 12, 12, tzinfo=pytz.UTC),
        )

        assert IngestionConfiguration.objects.filter(last_sync=_now).count() == 0

        video_return_value = [
            dict(
                title="Test one",
                authors=["Fernando McTest"],
                url="https://example.com/thing/one/",
                description="<p>Test description</p>",
                # image_url="https://example.com/one.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            )
        ]

        mock_fetch_external_data.return_value = video_return_value

        assert Video.objects.count() == 0
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)
        assert Video.objects.count() == 1
        assert not mock_send_notification.called  # This is what we care about here

    @mock.patch("developerportal.apps.ingestion.utils.fetch_external_data")
    @mock.patch("developerportal.apps.ingestion.utils.send_notification")
    def test_ingest_content__unhappy_path(
        self, mock_send_notification, mock_fetch_external_data
    ):

        mock_send_notification.return_value = False

        IngestionConfiguration.objects.all().delete()

        IngestionConfiguration.objects.create(
            source_name="One",
            source_url="https://example.com/one.xml",
            integration_type=IngestionConfiguration.CONTENT_TYPE_VIDEO,
            last_sync=datetime.datetime(12, 12, 12, tzinfo=pytz.UTC),
        )

        video_return_value = [
            dict(
                title="Test one",
                authors=["Fernando McTest"],
                url="https://example.com/thing/one/",
                description="<p>Test description</p>",
                # image_url="https://example.com/one.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            )
        ]

        mock_fetch_external_data.return_value = video_return_value

        assert Video.objects.count() == 0

        with self.assertLogs(
            "developerportal.apps.ingestion.utils", level="INFO"
        ) as cm:
            ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)
        assert Video.objects.count() == 1

        draft_page = Video.objects.filter(live=False).get()

        self.assertEqual(
            cm.output,
            [
                (
                    "INFO:developerportal.apps.ingestion.utils:Generating a "
                    "new draft using _make_video_page from "
                    "{'title': 'Test one', "
                    "'authors': ['Fernando McTest'], "
                    "'url': 'https://example.com/thing/one/', "
                    "'description': '<p>Test description</p>', "
                    "'timestamp': datetime.datetime(2020, 1, 10, 22, 47, 43, "
                    "tzinfo=<UTC>), 'owner': <User: ingestion_user>}"
                ),
                (
                    "WARNING:developerportal.apps.ingestion.utils:"
                    f"Failed to send notification that {draft_page} was created."
                ),
            ],
        )

    def test__get_factory_func(self):

        self.assertEqual(_get_factory_func("Video"), _make_video_page)
        self.assertEqual(
            _get_factory_func("ExternalArticle"), _make_external_article_page
        )

    def test__get_factory_func__raises_NotImplementedError(self):

        models = [Article, ExternalContent, ExternalVideo, ExternalEvent]

        for klass in models:
            with self.subTest(model_name=klass.__name__):
                with self.assertRaises(NotImplementedError):
                    _get_factory_func(model_name=klass.__name__)

    @mock.patch("developerportal.apps.ingestion.utils.requests.get")
    def test__store_external_image__local_filesystem(self, mock_requests_get):
        # This test is written assuming local file storage, even though
        # everything apart from CI will be using S3 as its backend. The function
        # HAS been tested with S3, though.
        assert (
            settings.DEFAULT_FILE_STORAGE
            == "django.core.files.storage.FileSystemStorage"
        )
        mock_response = mock.Mock()
        mock_response.content = image_one_bytearray
        mock_requests_get.return_value = mock_response

        saved_image = _store_external_image(image_url="https://example.com/test.png")

        mock_requests_get.assert_called_once_with("https://example.com/test.png")

        saved_image.file.open()
        saved_image.file.seek(0)
        comparison_content = saved_image.file.read()
        self.assertEqual(bytearray(comparison_content), image_one_bytearray)

    @mock.patch("developerportal.apps.ingestion.utils._store_external_image")
    def test_generate_draft_from_external_data__externalarticle(
        self, mock_store_external_image
    ):

        image = MozImage(width=1, height=1)
        image.save()
        mock_store_external_image.return_value = image

        data = dict(
            title="ECSY Developer tools extension",
            authors=["Fernando Serrano"],  # not used for now
            description="<p>Test description</p>",
            url="https://blog.mozvr.com/ecsy-developer-tools/",
            image_url="https://blog.mozvr.com/content/images/2019/12/ecsy-header.png",
            timestamp=datetime.datetime(2019, 12, 10, 22, 47, 43, tzinfo=pytz.UTC),
        )

        obj = generate_draft_from_external_data(
            factory_func=_make_external_article_page, data=data
        )
        obj.refresh_from_db()
        self.assertEqual(type(obj), ExternalArticle)
        self.assertEqual(obj.slug, "ecsy-developer-tools-extension-6705c559c5d3")
        self.assertEqual(obj.title, data["title"])
        self.assertEqual(obj.draft_title, data["title"])
        self.assertEqual(obj.external_url, data["url"])
        self.assertEqual(obj.date, data["timestamp"].date())
        mock_store_external_image.assert_called_once_with(data["image_url"])
        self.assertEqual(obj.card_image, image)
        self.assertFalse(obj.live)
        self.assertTrue(obj.has_unpublished_changes)
        self.assertTrue(obj.get_parent().slug == "root")

    @mock.patch("developerportal.apps.ingestion.utils._store_external_image")
    def test_generate_draft_from_external_data__video(self, mock_store_external_image):
        image = MozImage(width=1, height=1)
        image.save()
        mock_store_external_image.return_value = image

        data = dict(
            title="Where do Browser Styles Come From?",
            authors=["Mozilla Developer"],  # Not used for now
            url="https://www.youtube.com/watch?v=spK_S0HfzFw",
            description="<p>Test description</p>",
            image_url="https://i4.ytimg.com/vi/spK_S0HfzFw/hqdefault.jpg",
            timestamp=datetime.datetime(2019, 12, 11, 11, 0, 10, tzinfo=tzlocal()),
        )

        obj = generate_draft_from_external_data(
            factory_func=_make_video_page, data=data
        )
        obj.refresh_from_db()
        self.assertEqual(type(obj), Video)
        self.assertEqual(obj.slug, "where-do-browser-styles-come-from-cd6673c468b5")
        self.assertEqual(obj.title, data["title"])
        self.assertEqual(obj.draft_title, data["title"])
        self.assertEqual(obj.video_url[0].value.url, data["url"])
        self.assertEqual(obj.date, data["timestamp"].date())
        mock_store_external_image.assert_called_once_with(data["image_url"])
        self.assertEqual(obj.card_image, image)
        self.assertFalse(obj.live)
        self.assertTrue(obj.has_unpublished_changes)
        self.assertTrue(obj.get_parent().slug == "videos")

    def test_get_slug(self):

        cases = [
            {
                "input": {"title": "hello", "date": datetime.datetime(2002, 2, 2)},
                "expected": "hello-d15ff467e978",
            },
            {
                "input": {
                    "title": "Hello, world!"
                    * 25,  # definitely overflows 242 truncation threshold
                    "date": datetime.datetime(2012, 2, 2),
                },
                "expected": "{}-{}".format(
                    str("hello-world" * 25)[:242], "d7ddfd0ace8a"
                ),
            },
        ]
        for case in cases:
            with self.subTest(input_=case["input"], expected=case["expected"]):
                self.assertEqual(_get_slug(case["input"]), case["expected"])

    def test__get_item_description(self):

        cases = [
            {
                "input": "<h1>header</h1><p>test description</p>",
                "expected": "<p>test description</p>",
                "desc_": "skips header",
            },
            {
                "input": "<p>test description!</p><p>another thing</p>",
                "expected": "<p>test description!</p>",
                "desc_": "multiple p nodes",
            },
            {
                "input": "<h1>header</h1><p>test description",
                "expected": "<p>test description</p>",
                "desc_": "bad HTML 1 gets fixed",
            },
            {
                "input": "<h1>header</h1><p>test description!<p>another thing</p>",
                "expected": "<p>test description!</p>",
                "desc_": "bad HTML 2 gets fixed",
            },
            {
                "input": "<h1>header</h1><span>test description.<span>",
                "expected": "",
                "desc_": "No <p> node - skip it entirely",
            },
            {"input": "", "expected": "", "desc_": "Empty string"},
            {"input": None, "expected": "", "desc_": "Description is None"},
            {
                "input": f"<p>{ 'x' * 393}, but not this</p>",
                "expected": f"<p>{ 'x' * 393}</p>",
                "desc_": "<p> node > 400 chars gets cut, but still wrapped in <p>",
            },
            {
                "input": (
                    "<p>test description!&lt;marquee&gt;test&lt;/marquee&gt;</p>"
                ),
                "expected": (
                    "<p>test description!&lt;marquee&gt;test&lt;/marquee&gt;</p>"
                ),
                "desc_": "Already-escaped markup is retained",
            },
            {
                "input": "<p>test description!<marquee>test</marquee></p>",
                "expected": "<p>test description!test</p>",
                "desc_": "Unescaped markup is removed 1",
            },
            {
                "input": '<p>test description!<script>alert("boo");</script></p>',
                "expected": ('<p>test description!alert("boo");</p>'),
                "desc_": "Unescaped markup is removed 2",
            },
            {
                "input": '<script>alert("boo");</script>',
                "expected": (""),
                "desc_": "Unescaped markup is removed 3",
            },
            {
                "input": (
                    "<p>test description!"
                    "<script>"
                    '<script>alert("boo");</script>'
                    "</script>"
                    "</p>"
                ),
                "expected": (
                    '<p>test description!&lt;script&gt;alert("boo");</p>'
                    # Beautiful Soup drops the second </script> before we sanitise it
                ),
                "desc_": "Unescaped doubled-up markup is handled",
            },
            {
                "input": (
                    f"<p><script>alert('boo');</script>{ 'x' * 379}X, but not this</p>"
                ),
                "expected": (f"<p>alert('boo');{ 'x' * 379}X</p>"),
                "desc_": "Truncation and removal of unescaped content",
            },
        ]
        for case in cases:
            with self.subTest(label=case["desc_"]):

                mock_entry = mock.Mock(description=case["input"])
                assert mock_entry.description == case["input"]  # Confirm patch

                self.assertEqual(_get_item_description(mock_entry), case["expected"])
