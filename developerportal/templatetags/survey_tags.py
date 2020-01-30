from django import template
from django.conf import settings

import waffle

register = template.Library()


@register.inclusion_tag("survey.html", takes_context=True)
def survey_prompt(context):
    request = context["request"]

    survey_url = settings.TASK_COMPLETION_SURVEY_URL
    # If this is "undefined" in config, treat it as if absent
    if survey_url == "undefined":
        survey_url = None

    # Trigger the waffle flag check: IFF the flag is using a Percentage-based rule,
    # this will set the cookie that the client-side JS will look for
    waffle.flag_is_active(request, "show_task_completion_survey")
    return {"survey_url": survey_url}
