import logging
from multiprocessing import Process
import os

from django.conf import settings
from django.core.management import call_command
from django.utils.html import escape

from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtail.core.signals import page_published, page_unpublished


logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)


class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    # Other identifiers are available for other types of links.
    identifier = 'external'

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return '<a href="%s" class="external-link" target="_blank" rel="noopener noreferrer">' % escape(href)


@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


def _static_build_async(pipeline=settings.STATIC_BUILD_PIPELINE):
    """Calls each command in the static build pipeline in turn."""
    log_prefix = 'Static build task'
    for name, command in pipeline:
        if settings.DEBUG:
            logger.info(f'{log_prefix} ‘{name}’ skipped.')
        else:
            logger.info(f'{log_prefix} ‘{name}’ started.')
            call_command(command)
            logger.info(f'{log_prefix} ‘{name}’ finished.')


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals."""
    # Spawn a process to do the actual build.
    process = Process(target=_static_build_async)
    process.start()


page_published.connect(static_build)
page_unpublished.connect(static_build)
