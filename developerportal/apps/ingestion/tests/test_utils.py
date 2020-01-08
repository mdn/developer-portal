import datetime
from unittest import mock

from django.test import TestCase

import pytz
from dateutil.tz import tzlocal

from developerportal.apps.ingestion.utils import fetch_external_data, ingest_content

from ...externalcontent.models import ExternalArticle, ExternalVideo
from ..models import IngestionConfiguration


class UtilsTestCase(TestCase):

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

    @mock.patch("developerportal.apps.ingestion.utils.fetch_external_data")
    @mock.patch("developerportal.apps.ingestion.utils.tz_now")
    def test_ingest_content(self, mock_tz_now, mock_fetch_external_data):

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
                # image_url="https://example.com/one.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
            dict(
                title="Test two",
                authors=["Alice McTest"],
                url="https://example.com/thing/two/",
                # image_url="https://example.com/two.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
            dict(
                title="Test three",
                authors=["Mary McTest"],
                url="https://example.com/thing/three/",
                # image_url="https://example.com/three.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            ),
        ]

        mock_fetch_external_data.return_value = video_return_value

        # First try Video content
        assert ExternalVideo.objects.count() == 0
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)
        assert ExternalVideo.objects.count() == 3

        assert ExternalVideo.objects.filter(title="Test one").count() == 1
        assert ExternalVideo.objects.filter(title="Test two").count() == 1
        assert ExternalVideo.objects.filter(title="Test three").count() == 1

        # None of these has been published yet
        assert (
            ExternalVideo.objects.filter(first_published_at__isnull=True).count() == 3
        )

        article_return_value = video_return_value + [
            dict(
                title="Test four",
                authors=["Barry McTest"],
                url="https://example.com/thing/four/",
                # image_url="https://example.com/four.png",
                # Image ingestion is tested elsewhere
                timestamp=datetime.datetime(2020, 1, 10, 22, 47, 43, tzinfo=pytz.UTC),
            )
        ]
        for x in article_return_value:
            x["title"] += " for Video"

        mock_fetch_external_data.reset_mock()
        mock_fetch_external_data.return_value = article_return_value

        # Now try Article content
        assert ExternalArticle.objects.count() == 0
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_ARTICLE)
        assert ExternalArticle.objects.count() == 4

        assert ExternalArticle.objects.filter(title="Test one for Video").count() == 1
        assert ExternalArticle.objects.filter(title="Test two for Video").count() == 1
        assert ExternalArticle.objects.filter(title="Test three for Video").count() == 1
        assert ExternalArticle.objects.filter(title="Test four for Video").count() == 1

        # None of these has been published yet
        assert (
            ExternalArticle.objects.filter(first_published_at__isnull=True).count() == 4
        )

        assert IngestionConfiguration.objects.filter(last_sync=_now).count() == 2
