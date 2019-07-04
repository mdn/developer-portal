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

class GetStartedBlock(blocks.StructBlock):
    """Panel of content displayed on Topics Get Started organism, 1 to 3"""
    title = blocks.CharBlock()
    image = ImageChooserBlock()
    description = blocks.TextBlock()
    button_text = blocks.CharBlock()
    button_destination = blocks.PageChooserBlock()

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
    name = blocks.CharBlock()
    job_title = blocks.CharBlock()
    profile_picture = ImageChooserBlock()
