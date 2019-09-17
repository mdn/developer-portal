from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class ButtonBlock(blocks.StructBlock):
    """Content for a button."""

    text = blocks.CharBlock()
    page_link = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(
        required=False, help_text="External URL to link to instead of a page."
    )

    class Meta:
        icon = "link"
        template = "button_block.html"


class CodeSnippetBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        choices=[
            ("css", "CSS"),
            ("go", "Go"),
            ("html", "HTML"),
            ("js", "JavaScript"),
            ("python", "Python"),
            ("rust", "Rust"),
            ("ts", "TypeScript"),
        ]
    )
    code = blocks.TextBlock()

    class Meta:
        icon = "code"
        template = "code_snippet_block.html"


class TabbedPanelBlock(blocks.StructBlock):
    """Panel of content displayed on Topics Tabbed Panel organism, 1 to 3"""

    title = blocks.CharBlock()
    image = ImageChooserBlock()
    description = blocks.TextBlock()
    button_text = blocks.CharBlock()
    page_link = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(
        required=False, help_text="External URL to link to instead of a page."
    )


class AgendaItemBlock(blocks.StructBlock):
    """Content for an event agenda item"""

    start_time = blocks.TimeBlock()
    end_time = blocks.TimeBlock(required=False)
    title = blocks.CharBlock()
    speaker = blocks.PageChooserBlock(required=False, page_type="people.Person")
    external_speaker = blocks.StructBlock(
        [
            ("name", blocks.CharBlock(required=False)),
            ("url", blocks.URLBlock(label="URL", required=False)),
        ]
    )


class ExternalLinkBlock(blocks.StructBlock):
    """Content for a link to an external page without an image,
    e.g. MDN related links."""

    title = blocks.CharBlock(label="Name")
    url = blocks.URLBlock()


class ExternalSpeakerBlock(blocks.StructBlock):
    """Content for an external speaker, displayed on event page"""

    title = blocks.CharBlock(label="Name")
    job_title = blocks.CharBlock()
    image = ImageChooserBlock()
    url = blocks.URLBlock(label="URL", required=False)


class ExternalAuthorBlock(blocks.StructBlock):
    """Content for an external author, for an internal or external article"""

    title = blocks.CharBlock(label="Name")
    image = ImageChooserBlock()
    url = blocks.URLBlock(label="URL", required=False)


class FeaturedExternalBlock(blocks.StructBlock):
    """Content for a link to an external page displayed as featured card"""

    url = blocks.URLBlock()
    title = blocks.CharBlock()
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock()


class PersonalWebsiteBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="URL")
    title = blocks.CharBlock(required=False)
    icon = ImageChooserBlock(required=False)

    class Meta:
        help_text = (
            "Details of any other personal website, to be displayed alongside "
            "social profiles."
        )
