# pylint: disable=no-member
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import escape, format_html

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler


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
            '<a href="%s" target="_blank" rel="nofollow noopener noreferrer">'
            % escape(href)
        )


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)


@hooks.register("register_rich_text_features")
def register_button_section_feature(features):
    """Support marking a group of links as buttons within Draftail (which can then be
    styled with custom CSS in the Admin) + ensure the block enclosing the links is
    rendered with a custom CSS class we can target in the published page."""

    feature_name = "button-block"
    type_ = "button-block"
    tag = "div"
    # The value of _type contributes to an Admin CSS classname
    # of `.Draftail-block--button-block`

    control = {
        "type": type_,
        "label": "",
        "description": "Add a block will that render any links inside it as buttons",
        "element": "div",
        "icon": "icon icon-placeholder",
    }
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.BlockFeature(control)
    )
    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {tag: BlockElementHandler(type_)},
            "to_database_format": {
                "block_map": {
                    type_: {
                        "element": "div",
                        "props": {
                            "class": "links-as-buttons"
                        },  # This CSS class is what's used on the rendered page
                    }
                }
            },
        },
    )
    features.default_features.append("button-block")


@hooks.register(
    "insert_global_admin_css", order=10
)  #  positive int for `order` means it will run after Wagtail core
def global_admin_css():
    """Slot in custom CMS CSS to render the above button-block element nicely."""
    return format_html(
        '<link rel="stylesheet" href="{}">', static("css/admin_extras.css")
    )
