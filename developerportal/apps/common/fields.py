from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock


RICH_TEXT_FEATURES = (
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
        super(CustomStreamField, self).__init__([
            ('paragraph', RichTextBlock(features=RICH_TEXT_FEATURES)),
            ('image', ImageChooserBlock()),
        ], **dict(default=None, **kwargs))
