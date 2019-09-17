import binascii
import os

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from mimetypes import guess_type


register = template.Library()


@register.simple_tag
def make_list_from_args(*items):
    return [item for item in items if item]


@register.simple_tag
def mime_type(file_name):
    _mime_type, _ = guess_type(file_name)
    return _mime_type


@register.simple_tag
def random_hash():
    return binascii.hexlify(os.urandom(16)).decode("utf-8")


@register.simple_tag
def render_svg(f):
    return mark_safe(f.read().decode("utf-8"))


@register.simple_tag
def render_gif(block_value):
    if hasattr(block_value, "file") and hasattr(block_value.file, "name"):
        file_url = settings.MEDIA_URL + block_value.file.name
        return mark_safe(f'<img src="{file_url}" alt="">')
