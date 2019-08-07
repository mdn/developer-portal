from itertools import chain
from operator import attrgetter
from wagtail.core.models import Page

from django.apps import apps


def _combined_query(models, fn):
    """Execute callback `fn` for each model and chain the resulting querysets."""
    return chain.from_iterable([fn(_resolve_model(m)) for m in models])


def _resolve_model(model):
    """Given an 'app.Model' string or model return a model."""
    return apps.get_model(model) if isinstance(model, str) else model


def get_resources(page, models, filters=None, order_by=None, reverse=False):
    """Get resources for provided models matching filters.

    Params:
        page - the current page, used to exclude from queries.
        models - a list of app.model strings, or Models.
        filters - optional dictionary of queryset filters.
        order_by - key to order the combined set by, must be common to all models.
        reverse - whether to reverse the combined set, default false.
    """
    callback = lambda model: model.objects.filter(**filters).public().live().not_page(page).specific()
    result = _combined_query(models, callback)
    return sorted(result, key=attrgetter(order_by), reverse=reverse)


def get_combined_articles(page, **filters):
    """Get internal and external articles matching filters."""
    return get_resources(page, [
        'articles.Article',
        'externalcontent.ExternalArticle',
    ], filters=filters, order_by='date', reverse=True)


def get_combined_articles_and_videos(page, **filters):
    """Get internal and external articles and videos matching filters."""
    return get_resources(page, [
        'articles.Article',
        'videos.Video',
        'externalcontent.ExternalArticle',
        'externalcontent.ExternalVideo',
    ], filters=filters, order_by='date', reverse=True)


def get_combined_events(page, **filters):
    """Get internal and external events matching filters."""
    return get_resources(page, [
        'events.Event',
        'externalcontent.ExternalEvent',
    ], filters=filters, order_by='start_date')


def get_combined_videos(page, **filters):
    """Get internal and external videos matching filters."""
    return get_resources(page, [
        'videos.Video',
        'externalcontent.ExternalVideo',
    ], filters=filters, order_by='date', reverse=True)
