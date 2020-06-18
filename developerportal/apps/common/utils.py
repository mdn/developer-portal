import datetime
from itertools import chain
from operator import attrgetter
from urllib.parse import unquote

from django.apps import apps
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.timezone import now as tz_now

import bleach


def _combined_query(models, fn):
    """Execute callback `fn` for each model and chain the resulting querysets."""
    return chain.from_iterable([fn(_resolve_model(m)) for m in models])


def _resolve_model(model):
    """Given an 'app.Model' string or model return a model."""
    return apps.get_model(model) if isinstance(model, str) else model


def prep_search_terms(terms: str, use_bleach=True) -> str:
    """Fix up provided terms ready for passing to Wagtail's .search() model
    manager method. Note that at a lower level, for safety, the postgres_search
    backend ALSO does escaping and quoting for us: See Lexeme().as_sql() in
    https://github.com/wagtail/wagtail/blob/master/wagtail/contrib/postgres_search/query.py  # noqa
    """

    terms = unquote(terms)
    NON_SPACE_WHITESPACE = "\n\t\r"
    terms = terms.translate(str.maketrans("", "", NON_SPACE_WHITESPACE))
    if use_bleach:
        # if the following is removed, check/update app_tags.selected_filter_summary
        terms = bleach.clean(terms)
    terms = terms.strip()
    return terms


def get_resources(
    page,
    models,
    filters=None,
    q_object=None,
    search_terms=None,
    order_by=None,
    reverse=False,
):
    """Get resources for provided models matching filters.

    Params:
        page - the current page, used to exclude from queries.
        models - a list of app.model strings, or Models.
        filters - optional dictionary of queryset filters.
        search_terms - optional string of search terms
        q_object - optional way to run a more complex query
        order_by - key to order the combined set by, must be common to all models.
        reverse - whether to reverse the combined set, default false.
    """

    def callback(model):
        qs = model.published_objects
        if q_object:
            qs = qs.filter(q_object)

        qs = qs.filter(**filters).not_page(page).specific()

        if search_terms:
            # This has to come after .filter() because PostgresSearchResults
            # does not offer .filter() as a method
            qs = qs.search(prep_search_terms(search_terms))
        return qs

    result = _combined_query(models, callback)
    return sorted(set(result), key=attrgetter(order_by), reverse=reverse)


def get_combined_articles(page, **filters):
    """Get internal and external articles matching filters."""
    return get_resources(
        page,
        ["articles.Article", "externalcontent.ExternalArticle"],
        filters=filters,
        order_by="date",
        reverse=True,
    )


def get_combined_articles_and_videos(page, q_object=None, search_terms=None, **filters):
    """Get internal and external articles and videos matching filters."""
    return get_resources(
        page,
        [
            "articles.Article",
            "videos.Video",
            "externalcontent.ExternalArticle",
            "externalcontent.ExternalVideo",
        ],
        filters=filters,
        q_object=q_object,
        search_terms=search_terms,
        order_by="date",
        reverse=True,
    )


def get_combined_events(
    page, reverse=False, q_object=None, search_terms=None, **filters
):
    """Get internal and external events matching filters."""

    return get_resources(
        page,
        ["events.Event", "externalcontent.ExternalEvent"],
        filters=filters,
        q_object=q_object,
        search_terms=search_terms,
        order_by="start_date",
        reverse=reverse,
    )


def get_combined_videos(page, **filters):
    """Get internal and external videos matching filters."""
    return get_resources(
        page,
        ["videos.Video", "externalcontent.ExternalVideo"],
        filters=filters,
        order_by="date",
        reverse=True,
    )


def get_past_event_cutoff():
    # A safe datetime that defines when 'past' has happened
    # so we don't stop showing events too soon
    return (tz_now() - datetime.timedelta(days=1)).date()


def paginate_resources(resources, per_page, page_ref):
    paginator = Paginator(resources, per_page)
    try:
        resources = paginator.page(page_ref)
    except EmptyPage:
        # ie, out of range - get the last page
        resources = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # ie, `page_ref` is None or there's bad input
        resources = paginator.page(1)

    return resources
