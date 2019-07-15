import logging

from django.utils.html import escape
from django.core.management import call_command

from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtail.core.signals import page_published, page_unpublished


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


def build_static(*args, **kwargs):
    if production.DEBUG:
        logging.info('Building site')
        call_command('build')
        logging.info('Uploading site')
        call_command('aws_static')
    else:
        logging.info('Sorry we’re not building because of DEBUG.')


page_published.connect(build_static)
page_unpublished.connect(build_static)
