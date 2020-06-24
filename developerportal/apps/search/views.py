from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query


def site_search(request, template_name="site-search.html"):
    "Whole-site search view"
    search_query = request.GET.get("query", None)
    if search_query:
        search_results = Page.objects.live().search(search_query)

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = Page.objects.none()

    # Render template
    return render(
        request,
        template_name,
        {"search_query": search_query, "search_results": search_results},
    )
