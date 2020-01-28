from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("survey.html", takes_context=True)
def survey_prompt(context):
    request = context["request"]
    return {
        "request": request,  #  Needed by django-waffle in survey.html
        "survey_url": settings.TASK_COMPLETION_SURVEY_URL,
    }
