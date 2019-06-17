from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.blocks import RichTextBlock, RawHTMLBlock
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


RICH_TEXT_FEATURES = (
    # heading elements
    'h2',
    'h3',
    'h4',

    # inline
    'bold',
    'italic',
    'link',

    # lists
    'ol',
    'ul',

    # block
    'blockquote',
    'code',
    'hr',
)


class CustomStreamField(StreamField):
    def __init__(self, *args, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = None

        super().__init__([
            ('paragraph', RichTextBlock(features=RICH_TEXT_FEATURES)),
            ('image', ImageChooserBlock()),
            ('embed', EmbedBlock()),
            ('RawHtml', RawHTMLBlock(help_text='Adds Raw HTML to page, WARNING ! Code injects are possable')),

        ], **kwargs)
