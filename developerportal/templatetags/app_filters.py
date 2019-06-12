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
