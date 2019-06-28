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

class FeaturedExternalBlock(blocks.StructBlock):
    """Content for a link to an external page displayed as featured card"""
    url = blocks.URLBlock()
    title = blocks.CharBlock()
    intro = blocks.TextBlock(required=False)
    header_image = ImageChooserBlock(label='Image')

