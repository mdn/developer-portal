from typing import List

from django.conf import settings
from django.core.cache import cache

from ..articles.models import Articles
from ..events.models import Events
from ..home.models import HomePage
from ..people.models import People
from ..topics.models import Topics
from ..videos.models import Videos

PAGE_IDS_TO_EXCLUDE_CACHE_KEY = "pages-not-to-search"


def get_page_ids_to_omit_from_site_search() -> List[int]:
    """We dont want the site search to return certain pages that have no directly
    relevant content but which still might match on their title or description"""

    page_ids_to_exclude = cache.get(PAGE_IDS_TO_EXCLUDE_CACHE_KEY, [])

    if not page_ids_to_exclude:

        for model in (Articles, Events, HomePage, People, Topics, Videos):

            # There will be only one of each of these pages, but we don't want to
            # use get() as that would blow up site search if one section was removed
            instance = model.objects.first()
            if instance:
                page_ids_to_exclude.append(instance.id)

        page_ids_to_exclude.sort()

        cache.set(
            PAGE_IDS_TO_EXCLUDE_CACHE_KEY,
            page_ids_to_exclude,
            settings.CACHE_TIME_MEDIUM,
        )

    return page_ids_to_exclude
