import binascii
import os
import random

from django import template
from django.template.loader import get_template
from developerportal.apps.topics.models import Topic
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def render_nav(context, **kwargs):
    context['nav_items'] = Topic.objects.filter(show_in_menus=True).live().public()
    template_context = context.flatten()
    nav_template = get_template('molecules/header-nav.html')
    return nav_template.render(template_context)

@register.simple_tag
def render_svg(f):
    return mark_safe(f.read().decode('utf-8'))

@register.simple_tag
def random_hash():
    return binascii.hexlify(os.urandom(16)).decode('utf-8')
