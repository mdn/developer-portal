import logging

import waffle

from .constants import WAFFLE_FLAG_TASK_COMPLETION

logger = logging.getLogger(__name__)


def survey_waffle_flag_cdn_middleware(get_response):
    """Custom middleware to mitigate undesired behaviour by the CDN regarding
    django-waffle flags for the user-task-completion survey behaviour"""

    def middleware(request):
        # Suspending Caching Based on Cookies
        # If you want CloudFront to temporarily stop caching cookies and cookie
        # attributes, configure your origin server to add the following header
        # in responses to CloudFront: `no-cache="Set-Cookie"`

        # In survey_tags.py, django-waffle will set a cookie as a result of checking
        # a flag. (It sets it either way, with a True or False value, depending on
        # whether we should show the survey to the user).
        # But there's a problem: if there's no cookie set on a request, Cloudfront wants
        # to cache this response as something it can use _any_ time it gets a
        # no-waffle-cookie request (and Cloudfront caches responses against a key
        # based on {request + cookies}, _not_ on {response + cookies}).
        #
        # So, to deal with that, the _first_ time we are setting that a waffle cookie
        # for a user, we will tell CloudFront not to cache the cookies AND not to
        # cache the response.
        #
        # This should mean that:
        # - if someone shows up with no waffle cookie set, we don't cache what
        #   they get back, but their next request will include a cookie that suits
        #   what they are supposed to get from Origin
        # - when we get a request WITH a waffle cookie of a certain value, if we have
        #   a match in the CDN cache, we CAN return it, and if we don't have a match
        #   the CDN will get it from Origin and cache it based on the request params,
        #   which is fine

        _template = waffle.utils.get_setting("COOKIE")  # gets configured, else default
        task_completion_waffle_cookie_name = _template % WAFFLE_FLAG_TASK_COMPLETION

        request_had_survey_waffle_cookie = (
            # Presence of a cookie is enough - its value could be True or False,
            # but that's not important to us here
            task_completion_waffle_cookie_name
            in request.COOKIES
        )

        response = get_response(request)

        if not request_had_survey_waffle_cookie:
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
        return response

    return middleware
