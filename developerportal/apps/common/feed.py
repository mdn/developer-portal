from itertools import chain

from django.conf import settings
from django.contrib.syndication.views import Feed

from developerportal.apps.articles.models import Article
from developerportal.apps.videos.models import Video


class RssFeeds(Feed):
    title = "Mozilla Developer posts feed"
    link = "/posts-feed/"
    description = "Posts and Videos published"

    def items(self):
        items = sorted(
            chain(
                # Order here matters because we want Articles to come ahead of Videos.
                # Also, we sort by -date here BEFORE reversing so we can
                # appropriately truncate the queryset (and get newer ones
                # rather than older ones) instead of pull all of the items.
                Article.published_objects.all().order_by("-date")[
                    : settings.RSS_MAX_ITEMS
                ],
                Video.published_objects.all().order_by("-date")[
                    : settings.RSS_MAX_ITEMS
                ],
            ),
            key=lambda instance: instance.date,
            reverse=True,
        )
        return items[: settings.RSS_MAX_ITEMS]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
