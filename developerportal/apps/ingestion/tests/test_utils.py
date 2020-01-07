import datetime

from django.test import TestCase

import pytz
from dateutil.tz import tzlocal

from developerportal.apps.ingestion.utils import fetch_external_data


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
