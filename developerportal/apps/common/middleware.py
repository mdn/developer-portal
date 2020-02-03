import logging

from django.http import HttpRequest

import waffle

from .constants import WAFFLE_FLAG_TASK_COMPLETION

logger = logging.getLogger(__name__)


def waffle_flag_enabled_with_percentage_rule(
    request: HttpRequest, flag_name: str
) -> bool:
    """For the given Flag name, return True if it is ONLY configured for use
    using a Percent rule, else False - because none of the other configurations
    will be setting a waffle cookie, so we don't want to count them as valid.
    """

    # See Flag.is_active() to better understand how we're repurposing its logic here
    # https://github.com/django-waffle/django-waffle/blob/master/waffle/models.py#L250

    flag = waffle.models.Flag.objects.filter(name=flag_name).first()
    if not flag:
        return False

    if flag.testing:
        return False

    if flag.everyone is not None:
        return False

    active_for_language = flag._is_active_for_language(request)
    if active_for_language is not None:
        return False

    active_for_user = flag._is_active_for_user(request)
    if active_for_user is not None:
        return False

    if flag.percent and flag.percent > 0:
        return True

    return False


def request_had_survey_waffle_cookie(request: HttpRequest) -> bool:
    """Determine whether the HTTPRequest contains a waffle cookie for the survey"""

    _template = waffle.utils.get_setting("COOKIE")  # gets configured, else default
    task_completion_waffle_cookie_name = _template % WAFFLE_FLAG_TASK_COMPLETION
    # Presence of a cookie is enough - its value could be True or False,
    # but that's not important to us here
    return task_completion_waffle_cookie_name in request.COOKIES


def survey_waffle_flag_cdn_middleware(get_response):
    """Custom middleware to mitigate undesired behaviour by the CDN regarding
    django-waffle flags for the user-task-completion survey behaviour"""

    def middleware(request):

        """Conditionally disable CDN cacheing for certain responses, to avoid
        inappropriate content being cached against particular requests.

        Context:

        In survey_tags.py, django-waffle will set a cookie as a result of checking
        a flag. (It sets it either way, with a True or False value, depending on
        whether we should show the survey to the user).
        But there's a problem: if there's no cookie set on a request, Cloudfront wants
        to cache this response as something it can use _any_ time it gets a
        no-cookie request (ie: Cloudfront caches responses against a key
        based on {request + cookies}, _not_ on {response + cookies}).

        So, to deal with that, the _first_ time we are setting a waffle cookie
        for a user, we will tell CloudFront not to cache the cookies AND not to
        cache the response.

        This should mean that:
        - if someone shows up with no waffle cookie set, we don't cache what
          they get back, but their next request will include a cookie that suits
          what they are supposed to get from Origin
        - when we get a request WITH a waffle cookie of a certain value, if we have
          a match in the CDN cache, we CAN return it, and if we don't have a match
          the CDN will get it from Origin and cache it based on the request params,
          which is fine.

        IMPORTANT: when/if we add more cookies to the project, we should take care
        to ensure that we're not falling foul of a variation of this same problem.
        If that becomes the case, it might be simply that we can say "if there are no
        cookies (of ANY kind) in a request, _and_ we're setting ANY new cookie in the
        response, don't cache that response. (ie, update/replace the checks made using
        waffle_flag_enabled_with_percentage_rule and request_had_survey_waffle_cookie
        to decide when to execute the truthiest path, below.
        """

        response = get_response(request)

        if waffle_flag_enabled_with_percentage_rule(
            request, WAFFLE_FLAG_TASK_COMPLETION
        ):
            logger.info(
                f"Waffle Flag {WAFFLE_FLAG_TASK_COMPLETION} is using a Percent rule."
            )
            if not request_had_survey_waffle_cookie(request):
                logger.info(
                    "Request lacked a survey waffle cookie: "
                    "telling CDN not to cache response"
                )
                # No waffle cookie on the way in? We don't want this cached in the CDN
                response["Cache-Control"] = "no-cache"
                response["no-cache"] = "Set-Cookie"
            else:
                logger.info(
                    "Request had a survey waffle cookie: allowing CDN to cache response"
                )
        else:
            logger.info(
                (
                    f"Waffle Flag {WAFFLE_FLAG_TASK_COMPLETION} is not "
                    "using a Percent rule, so no need to modify CDN cacheing"
                )
            )

        return response

    return middleware
