from django import template
from django.template.defaultfilters import register

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)