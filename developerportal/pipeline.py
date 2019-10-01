import os

from django.conf import settings
from django.contrib import messages

import urllib3
from social_core.exceptions import AuthException


class InvalidUserOrgs(AuthException):
    def __str__(self):
        return "User is not part of an allowed organization."


GITHUB_API_BASE = "https://api.github.com"
# Pass multiple orgs in env separated by comma, e.g. GITHUB_ORGS=mdn,foo,bar
GITHUB_ORGS = os.environ.get("GITHUB_ORGS", "mdn").split(",")


def github_user_allowed(backend, details=None, response=None, *args, **kwargs):
    """Check if the GitHub user meets login requirements."""
    # Skip GitHub user checks if running in debug
    if settings.DEBUG:
        return

    http = urllib3.PoolManager()

    token = response["access_token"]
    username = details["username"]
    user_allowed = False

    for org in GITHUB_ORGS:
        url = f"{GITHUB_API_BASE}/orgs/{org}/members/{username}"
        response = http.request(
            "GET",
            url,
            headers={
                "Authorization": f"token {token}",
                "User-Agent": settings.WAGTAIL_SITE_NAME,
            },
        )
        # GitHub will only return a 204 if the user is a member of the org
        # https://developer.github.com/v3/orgs/members/#check-membership
        if response.status == 204:
            user_allowed = True

    # If user is still not allowed raise an exception to bail the auth pipeline
    if not user_allowed:
        raise InvalidUserOrgs(backend)


def success_message(is_new=False, request=None, user=None, *args, **kwargs):
    """Adds newly created users to Wagtail’s ‘Moderators’ permission group."""
    if is_new:
        if settings.DEBUG:  # Grant user superuser access if running in debug
            user.is_superuser = True
            user.save()
        else:  # Otherwise inform the user they need to contact an admin
            messages.success(
                request,
                (
                    "Success! You have been registered. Please contact an "
                    "administrator to complete your registration."
                ),
            )
