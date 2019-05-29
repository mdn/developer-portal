from django import template
from django.template.loader import get_template
from developerportal.apps.topics.models import Topic

register = template.Library()

@register.simple_tag(takes_context=True)
def render_nav(context, **kwargs):
    context['nav_items'] = Topic.objects.filter(show_in_menus=True).live().public()
    template_context = context.flatten()
    nav_template = get_template('molecules/header-nav.html')
    return nav_template.render(template_context)
