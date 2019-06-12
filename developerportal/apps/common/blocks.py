from wagtail.core import blocks

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

