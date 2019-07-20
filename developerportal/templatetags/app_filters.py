import pygments
from pygments import lexers
from pygments import formatters

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import register

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)

@register.filter(name='syntax_highlight', is_safe=True)
def syntax_highlight(value, language):
    lexer = lexers.get_lexer_by_name(language)
    output = pygments.highlight(value, lexer, formatters.HtmlFormatter(cssclass="syntax"))
    return mark_safe(output)

@register.filter(name='hex_to_rgb')
def hex_to_rgb(hex, format_string='rgb({r}, {g}, {b})'):
    """Returns the RGB value of a hexadecimal color."""
    hex = hex.replace('#', '')
    out = {
        'r': int(hex[0:2], 16),
        'g': int(hex[2:4], 16),
        'b': int(hex[4:6], 16),
    }
    return format_string.format(**out)
