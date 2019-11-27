import binascii
import os
from mimetypes import guess_type

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


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
