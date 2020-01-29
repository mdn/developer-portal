from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("survey.html", takes_context=True)
def survey_prompt(context):
    request = context["request"]

    survey_url = settings.TASK_COMPLETION_SURVEY_URL
    # If this is "undefined" in config, treat it as if absent
    if survey_url == "undefined":
        survey_url = None

    return {
        "request": request,  #  Needed by django-waffle in survey.html
        "survey_url": survey_url,
    }
