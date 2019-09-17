from wagtail.core.blocks import RawHTMLBlock, RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .blocks import ButtonBlock, CodeSnippetBlock
from .constants import RICH_TEXT_FEATURES


class CustomStreamField(StreamField):
    def __init__(self, *args, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = None

        super().__init__(
            [
                ("paragraph", RichTextBlock(features=RICH_TEXT_FEATURES)),
                ("image", ImageChooserBlock()),
                ("button", ButtonBlock()),
                ("embed", EmbedBlock()),
                (
                    "embed_html",
                    RawHTMLBlock(
                        help_text=(
                            "Warning: be careful what you paste here, since this "
                            "field could introduce XSS (or similar) bugs. "
                            "This field is meant solely for third-party embeds."
                        )
                    ),
                ),
                ("code_snippet", CodeSnippetBlock()),
            ],
            **kwargs
        )
