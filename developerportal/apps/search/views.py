from django.shortcuts import render

from wagtail.core.models import Page

from ..common.constants import PAGINATION_QUERYSTRING_KEY, SEARCH_QUERYSTRING_KEY
from ..common.utils import paginate_resources, prep_search_terms
from ..search.utils import get_page_ids_to_omit_from_site_search

SEARCH_RESULTS_PAGE_SIZE = 15


def site_search(request, template_name="site-search.html"):
    "Whole-site search view"
    search_query = request.GET.get(SEARCH_QUERYSTRING_KEY, None)
    if search_query:

        search_results = (
            Page.objects.public()
            .live()
            .exclude(id__in=get_page_ids_to_omit_from_site_search())
            .search(prep_search_terms(search_query))
        )
    else:
        search_results = Page.objects.none()

    total_results = search_results.count()

    search_results = paginate_resources(
        search_results,
        page_ref=request.GET.get(PAGINATION_QUERYSTRING_KEY),
        per_page=SEARCH_RESULTS_PAGE_SIZE,
    )

    # Render template
    return render(
        request,
        template_name,
        {
            "search_query": search_query,
            "total_results": total_results,
            "search_results": search_results,
        },
    )
