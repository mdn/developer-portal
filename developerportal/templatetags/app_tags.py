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


@register.simple_tag(takes_context=True)
def person_profile_picture_overlay(context, **kwargs):
    template_context = context.flatten()
    num = random.choice([1,2,3])
    template_name = "atoms/img/person-overlay-" + str(num) + ".svg"
    overlay_template = get_template(template_name)
    return overlay_template.render(template_context)
