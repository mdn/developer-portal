import binascii
import os
import random

from django import template
from django.template.loader import get_template
from developerportal.apps.topics.models import Topic
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def render_svg(f):
    return mark_safe(f.read().decode('utf-8'))


@register.simple_tag
def random_hash():
    return binascii.hexlify(os.urandom(16)).decode('utf-8')
