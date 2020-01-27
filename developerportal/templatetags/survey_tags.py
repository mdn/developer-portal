from django import template

register = template.Library()


@register.inclusion_tag("survey.html")
def survey_prompt():
    return {}
