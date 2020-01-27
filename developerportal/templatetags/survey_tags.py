from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("survey.html")
def survey_prompt():
    return {"survey_url": settings.TASK_COMPLETION_SURVEY_URL}
