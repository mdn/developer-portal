import binascii
import logging
import os
import re
from mimetypes import guess_type
from urllib.parse import quote_plus

from django import template
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe

from bs4 import BeautifulSoup
from developerportal.apps.common.constants import (
    DATE_PARAMS_QUERYSTRING_KEY,
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_PRODUCTION,
    ENVIRONMENT_STAGING,
    LOCATION_QUERYSTRING_KEY,
    ROLE_QUERYSTRING_KEY,
    SEARCH_QUERYSTRING_KEY,
    TOPIC_QUERYSTRING_KEY,
)

register = template.Library()

logger = logging.getLogger(__name__)


@register.simple_tag
def make_list_from_args(*items):
    return [item for item in items if item]


@register.simple_tag
def mime_type(file_name):
    _mime_type, _ = guess_type(file_name)
    return _mime_type


@register.simple_tag
def random_hash(start_with_letter=True):
    val = binascii.hexlify(os.urandom(15)).decode("utf-8")
    if start_with_letter:
        # If used as an XML or SVG `id` attribute, it has to start with a letter
        val = f"a{val}"
    return val


@register.simple_tag
def render_svg(f):
    return mark_safe(f.read().decode("utf-8"))


@register.filter
def to_svg(f):
    return render_svg(f)


@register.simple_tag
def render_gif(block_value):
    if hasattr(block_value, "file") and hasattr(block_value.file, "name"):
        file_url = settings.MEDIA_URL + block_value.file.name
        return mark_safe(f'<img src="{file_url}" alt="">')


@register.simple_tag
def get_scheme_and_host(request):
    return f"{request.scheme}://{request.get_host()}"


@register.simple_tag
def use_conventional_auth():
    return settings.USE_CONVENTIONAL_AUTH


@register.filter
def has_at_least_two_filters(filters):
    # For the given dictionary of `filters`, return True if at
    # least two of its keys' values are truthy, else False
    result = len([val for val in filters.values() if bool(val)]) >= 2
    return result


@register.filter
def filename_cachebreaker_to_querystring(url):
    """For the given URL, check if it has a cachebreaking hash. If it does,
    convert it to be a URLthat uses the hash as a querystring cachebreaker
    instead.

    eg
        INPUT: 'https://example.com/static/foo.12313abc.jpg'
        OUTPUT: 'https://example.com/static/foo.jpg?h=12313abc'

    Why? So that images automatically embedded in social media posts (via OG
    tags) don't end up as broken links with a new release that changes the hash
    in the filename -- by moving the hash to a querystring, we get the benefit
    of cachebreaking but with a much softer edge that won't result in links
    404ing even if the cachebreaking hash has changed. (ie, querystring
    cachebreakers are more forgiving.)

    Note that ManifestFileStorage (used by django-whitenoise in this project) makes
    hash-named versions of the files, but also _does_ keep the original around,
    so we are safe to assume that if static/img/foo.213123.jpg exists, then
    static/img/foo.jpg will, too
    """

    pattern = re.compile(r"(\.[a-f0-9]+)\.\w+$")
    hits = pattern.search(url)
    if not hits:
        logger.debug(f"Couldn't extract hash from URL {url}. Leaving unchanged.")
        return url
    dotted_hash = hits.groups()[0]
    url = url.replace(dotted_hash, "")
    _hash = dotted_hash[1:]  # the [1:] skips the . at the start
    url = f"{url}?h={_hash}"
    return url


@register.filter
def pagination_additional_filter_params(request):
    """Used to ensure the pagination links include any non-pagination
    querystrings in them, too.

    Note that the output always starts with & because the idea is that the
    resulting string is appended to a ?page=X querystring in the template
    """

    QUERY_PARAMS_TO_PASS_ON = (
        # PAGINATION_QUERYSTRING_KEY,  # we DON'T want this one: it's added separately
        TOPIC_QUERYSTRING_KEY,
        ROLE_QUERYSTRING_KEY,
        LOCATION_QUERYSTRING_KEY,
        DATE_PARAMS_QUERYSTRING_KEY,
        SEARCH_QUERYSTRING_KEY,
    )

    output_params_strings = []

    input_keys = request.GET.keys()

    for input_key in input_keys:
        if input_key not in QUERY_PARAMS_TO_PASS_ON:
            continue
        input_params = request.GET.getlist(input_key)
        for input_param in input_params:
            # Note that using `urllib.parse.quote_plus` avoids spaces appearing in
            # the output, which breaks Safari (because the space triggers a web
            # search, not a HTTP request to the site)
            output_params_strings.append(f"{input_key}={quote_plus(input_param)}")

    joined_params = "&".join(output_params_strings)
    if joined_params:
        joined_params = f"&{joined_params}"
    return joined_params


@register.simple_tag
def get_favicon_path():
    """Returns a path to the relevant favicon file, suitable for
    use with the {% static %} tag."""

    DEFAULT_FAVICON = "favicon.ico"
    spec = {
        ENVIRONMENT_DEVELOPMENT: "favicon_dev.ico",
        ENVIRONMENT_STAGING: "favicon_stage.ico",
    }
    filename = spec.get(settings.ACTIVE_ENVIRONMENT, DEFAULT_FAVICON)

    return f"img/icons/{filename}"


@register.simple_tag
def is_production_site():
    return settings.ACTIVE_ENVIRONMENT == ENVIRONMENT_PRODUCTION


@register.simple_tag
def get_menu_item_icon(page):
    icon_url = static("img/icons/default-d.svg")

    try:
        icon_url = page.icon.url
    except (AttributeError, ValueError):
        pass

    return icon_url


@register.simple_tag
def split_featured_items(iterable):
    """For the given `iterable`, return it split into two lists appropriate to
    the length of the iterable and compatible with a sensible HTML layout

    As such we return the following list of dicts, each containing a list and a total

    rows = [
        {
            items: <List>
            count: <int>
        },
        ...
    ]

    At the moment, `rows` will have one or two members

    Seven items:
        rows = [
            {
                items: [item_1 , item_2, item_3],
                count: 3
            },
            {
                items: [item_4, item_5, item_6, item_7],
                count: 4
            }
        ]

    Six items:
        rows = [
            {
                items: [item_1 , item_2, item_3],
                count: 3
            },
            {
                items: [item_4, item_5, item_6],
                count: 3
            }
        ]

    Five items:
        rows = [
            {
                items: [item_1 , item_2],
                count: 2
            },
            {
                items: [item_3 , item_4, item_5],
                count: 3
            }
        ]

    Four items:
        rows = [
            {
                items: [item_1 , item_2],
                count: 2
            },
            {
                items: [item_3 , item_4],
                count: 2
            }
        ]

    Three items:
        rows = [
            {
                items: [item_1 , item_2, item_3],
                count: 3
            },
        ]

    Two items:
        rows = [
            {
                items: [item_1 , item_2],
                count: 2
            },
        ]

    One item:
        rows = [
            {
                items: [item_1],
                count: 1
            },
        ]

    """
    output = []

    if len(iterable) in [6, 7]:
        # Two rows with 3 + 3 or 3 + 4
        output = [
            dict(items=iterable[:3], count=len(iterable[:3])),
            dict(items=iterable[3:], count=len(iterable[3:])),
        ]
    elif len(iterable) in [4, 5]:
        # Two rows with 2 + 2 or 2 + 3
        output = [
            dict(items=iterable[:2], count=len(iterable[:2])),
            dict(items=iterable[2:], count=len(iterable[2:])),
        ]
    else:
        # single row, the same length as the original iterable
        output = [dict(items=iterable, count=len(iterable))]

    return output


@register.simple_tag
def get_label_html(text: str, extra_css_classes: str = None) -> str:
    """Render the label atom HTML, using the provided `text`
    and adding `extra_css_classes` if need be"""
    return mark_safe(
        template.loader.render_to_string(
            "atoms/label.html",
            {"content": text, "extra_css_classes": extra_css_classes},
        )
    )


@register.simple_tag
def render_embed_with_fixups(page, embed_html):
    """Fix up iframe embeds for HTML validation and a11y improvements.

    * Embed iframes sometimes lack a title attribute, which hampers accessibility.
    This templatetag addresses that by adding the page's title as the iframe's
    title attribute.

    * Also, `frameborder` is not a valid attribute in HTML5, so throws an error
    when validated

    Hat-tip to https://github.com/wagtail/wagtail/issues/5982#issuecomment-625534509"""

    soup = BeautifulSoup(embed_html, "html.parser")
    try:
        iframe_tags = soup.find_all("iframe")
        for iframe_tag in iframe_tags:
            if not iframe_tag.get("title"):
                iframe_tag["title"] = page.title
            if iframe_tag.get("frameborder"):
                del iframe_tag["frameborder"]
        embed_html = soup.prettify()
    except (AttributeError, TypeError):
        pass

    return mark_safe(embed_html)
