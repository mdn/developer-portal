from django import template
from django.utils.safestring import mark_safe

import pygments
from pygments import lexers
from pygments import formatters


register = template.Library()


@register.filter(name='hex_to_rgb')
def hex_to_rgb(hex_color, alpha=1):
    """Returns the RGB value of a hexadecimal color."""
    hex_color = hex_color.replace('#', '')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    alpha = float(alpha)
    a = alpha if 0 < alpha < 1 else 1
    return f'rgb({r}, {g}, {b})' if a == 1 else f'rgb({r}, {g}, {b}, {a})'


@register.filter(name='syntax_highlight', is_safe=True)
def syntax_highlight(value, language):
    lexer = lexers.get_lexer_by_name(language)
    output = pygments.highlight(value, lexer, formatters.HtmlFormatter(cssclass="syntax"))
    return mark_safe(output)


@register.filter(name='times')
def times(number):
    return range(number)
