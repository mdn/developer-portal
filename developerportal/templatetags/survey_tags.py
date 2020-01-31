from django import template
from django.conf import settings

import waffle

from ..apps.common.constants import WAFFLE_FLAG_TASK_COMPLETION

register = template.Library()


@register.inclusion_tag("survey.html", takes_context=True)
def survey_prompt(context):

    request = context["request"]

    survey_url = settings.TASK_COMPLETION_SURVEY_URL
    # If this is "undefined" in config, treat it as if absent
    if survey_url == "undefined":
        survey_url = None

    # Trigger the waffle flag check: IFF the flag is using a Percentage-based rule,
    # this will set the cookie that the client-side JS will look for.
    # NB: see common.middleware.survey_waffle_flag_cdn_middleware for some
    # 'interesting' behaviour related to waffle flags

    waffle.flag_is_active(request, WAFFLE_FLAG_TASK_COMPLETION)
    return {"survey_url": survey_url}
