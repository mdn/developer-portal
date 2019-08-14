# pylint: disable=no-member
from django.db.utils import ProgrammingError
from django.utils.html import escape

from wagtail.core import hooks
from wagtail.core.models import Page, Site
from wagtail.core.rich_text import LinkHandler


class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    # Other identifiers are available for other types of links.
    identifier = 'external'

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs['href']
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return '<a href="%s" class="external-link" target="_blank" rel="noopener noreferrer">' % escape(href)


@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


def _custom_slug_help_text():
    # Generate slug help_text that uses the default site’s real URL, falling
    # back to example.com instead of the Wagtail default.
    default_site = Site.objects.filter(is_default_site=True).first()
    base_url = default_site.root_url if default_site else 'https://example.com'
    return f'The name of the page as it will appear in URLs e.g. for an article: {base_url}/articles/slug/'


try:
    # Apply the custom slug help text to all Page models
    slug_field = Page._meta.get_field('slug')
    slug_field.verbose_name = 'URL slug'
    slug_field.help_text = _custom_slug_help_text()
except ProgrammingError:
    # This will fail if core migrations have not yet been run
    pass
