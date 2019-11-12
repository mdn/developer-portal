from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.core.models import Site

EXTERNAL_ENTITY_NAMES = [
    # Done as strings to avoid cross-module imports
    "ExternalArticle",
    "ExternalContent",
    "ExternalEvent",
    "ExternalVideo",
]


def _custom_slug_help_text(model):
    """Helper to generate entity-appropriate help text without also triggering
    migration creation (which monkeypatching the models will do)"""

    if model.__class__.__name__ in EXTERNAL_ENTITY_NAMES:
        return (
            "Because you are adding External content, this slug will NOT be "
            "visible to the end user, but still needs to be unique within the CMS."
        )
    else:
        # Generate slug help_text that uses the default site’s real URL, falling
        # back to example.com instead of the Wagtail default.
        default_site = Site.objects.filter(is_default_site=True).first()
        base_url = default_site.root_url if default_site else "https://example.com"

        return (
            f"The name of the page as it will appear in URLs. For example, "
            f"for a post: {base_url}/posts/your-slug-here/"
        )


class BasePageForm(WagtailAdminPageForm):
    """Base form class to splice in special behaviour common to all forms

    Currently affects:
        - SlugField.help_text – adds a Site-aware URL instead of the Wagtail default
    """

    SLUGFIELD_NAME = "slug"  #  This is default for Wagtail's 'settings' tab

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Find the default slug field, if possible, and patch it
        slug_field = self.fields.get(self.SLUGFIELD_NAME)
        if slug_field:
            slug_field.help_text = _custom_slug_help_text(self.instance)
