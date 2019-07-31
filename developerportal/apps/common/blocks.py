from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

class CodeSnippetBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=[
        ('css', 'CSS'),
        ('go', 'Go'),
        ('html', 'HTML'),
        ('js', 'JavaScript'),
        ('python', 'Python'),
        ('rust', 'Rust'),
        ('ts', 'TypeScript'),
    ])
    code = blocks.TextBlock()

    class Meta:
        template = 'code_snippet_block.html'

class TabbedPanelBlock(blocks.StructBlock):
    """Panel of content displayed on Topics Tabbed Panel organism, 1 to 3"""
    title = blocks.CharBlock()
    image = ImageChooserBlock()
    description = blocks.TextBlock()
    button_text = blocks.CharBlock()
    page_link = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False, help_text='External URL to link to instead of a page.')

class AgendaItemBlock(blocks.StructBlock):
    """Content for an event agenda item"""
    start_time = blocks.TimeBlock()
    end_time = blocks.TimeBlock(required=False)
    title = blocks.CharBlock()
    speaker = blocks.PageChooserBlock(required=False, page_type='people.Person')
    external_speaker = blocks.StructBlock([
        ('name', blocks.CharBlock(required=False)),
        ('url', blocks.URLBlock(label='URL', required=False)),
    ])

class ExternalSpeakerBlock(blocks.StructBlock):
    """Content for an external speaker, displayed on event page"""
    title = blocks.CharBlock(label='Name')
    job_title = blocks.CharBlock()
    profile_picture = ImageChooserBlock()
    url = blocks.URLBlock(label='URL', required=False)

class FeaturedExternalBlock(blocks.StructBlock):
    """Content for a link to an external page displayed as featured card"""
    url = blocks.URLBlock()
    title = blocks.CharBlock()
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock()
