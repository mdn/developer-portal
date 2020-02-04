from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("survey.html")
def survey_prompt():

    survey_url = settings.TASK_COMPLETION_SURVEY_URL
    # If this is "undefined" in config, treat it as if absent
    if survey_url == "undefined":
        survey_url = None

    return {"survey_url": survey_url}
