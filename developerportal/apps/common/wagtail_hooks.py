# pylint: disable=no-member
from django.db.models.signals import post_save
from django.utils.html import escape

from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler

from waffle.models import Flag

from ..taskqueue.tasks import invalidate_entire_cdn
from .constants import WAFFLE_FLAG_TASK_COMPLETION


class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    # Other identifiers are available for other types of links.
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return (
            '<a href="%s" class="external-link" target="_blank" '
            'rel="noopener noreferrer">' % escape(href)
        )


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


def purge_cdn_when_whitelisted_waffle_flags_saved(signal, **kwargs):
    """Sometimes, when a waffle flag has been amended that sets a cookie,
    the cached state in the CDN is no longer a useful one. We should trigger
    an invalidation when such a flag is changed"""

    whitelist = [WAFFLE_FLAG_TASK_COMPLETION]

    instance = kwargs.get("instance")
    if instance and instance.name in whitelist:
        invalidate_entire_cdn.delay()


post_save.connect(purge_cdn_when_whitelisted_waffle_flags_saved, sender=Flag)
