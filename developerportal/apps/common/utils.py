from itertools import chain
from operator import attrgetter


def get_combined_articles(page, **filters):
    """Get Article and ExternalArticle instances matching given filters, if provided."""
    from ..articles.models import Article
    from ..externalcontent.models import ExternalArticle
    internal = Article.objects.filter(**filters).public().live().not_page(page).distinct()
    external = ExternalArticle.objects.filter(**filters).public().live().not_page(page).distinct()
    return sorted(chain(internal, external), key=attrgetter('date'), reverse=True)


def get_combined_events(page, **filters):
    """Get Event and ExternalEvent instances matching given filters, if provided."""
    from ..events.models import Event
    from ..externalcontent.models import ExternalEvent
    internal = Event.objects.filter(**filters).public().live().not_page(page).distinct()
    external = ExternalEvent.objects.filter(**filters).public().live().not_page(page).distinct()
    return sorted(chain(internal, external), key=attrgetter('start_date'))
