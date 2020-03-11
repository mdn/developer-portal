import logging

from django import template
from django.conf import settings

logger = logging.getLogger(__name__)
register = template.Library()


@register.inclusion_tag("survey.html")
def survey_prompt():

    survey_url = settings.TASK_COMPLETION_SURVEY_URL
    # If this is "undefined" in config, treat it as if absent
    if survey_url == "undefined":
        survey_url = None

    survey_percentage = settings.TASK_COMPLETION_SURVEY_PERCENTAGE
    return {"survey_url": survey_url, "survey_percentage": survey_percentage}
