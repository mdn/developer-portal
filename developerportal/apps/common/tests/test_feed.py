import datetime

from django.test import TestCase, override_settings

from developerportal.apps.articles.models import Article
from developerportal.apps.common.feed import RssFeeds
from developerportal.apps.videos.models import Video


class RSSFeedsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.video_newer = Video.objects.create(
            title="Video Newer",
            path="000100010004",
            depth=6,
            date=datetime.date(2019, 10, 1),
        )
        cls.video_older = Video.objects.create(
            title="Video Older",
            path="000100010002",
            depth=6,
            date=datetime.date(2019, 6, 1),
        )
        cls.video_oldest = Video.objects.create(
            title="Video Oldest",
            path="000100010001",
            depth=6,
            date=datetime.date(2019, 1, 1),
        )

        cls.article_newer = Article.objects.create(
            title="Article Newer",
            path="000100010007",
            depth=6,
            date=datetime.date(2019, 10, 1),
        )
        cls.article_older = Article.objects.create(
            title="Article Older",
            path="000100010005",
            depth=6,
            date=datetime.date(2019, 6, 1),
        )
        cls.article_oldest = Article.objects.create(
            title="Article Oldest",
            path="000100010003",
            depth=6,
            date=datetime.date(2019, 1, 1),
        )

    def test_feed_ordering(self):
        # Show newer comes ahead of older ones, and that Articles come ahead of Videos
        assert RssFeeds().items() == [
            self.article_newer,
            self.video_newer,
            self.article_older,
            self.video_older,
            self.article_oldest,
            self.video_oldest,
        ]

    @override_settings(RSS_MAX_ITEMS=3)
    def test_limit_to_feed(self):
        assert RssFeeds().items() == [
            self.article_newer,
            self.video_newer,
            self.article_older,
        ]
