from wagtail.core import blocks

class CodeSnippetBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=[
      ('python', 'Python'),
      ('rust', 'Rust'),
      ('js', 'JavaScript'),
      ('ts', 'TypeScript'),
      ('go', 'Go'),
      ('haskell', 'Haskell'),
    ])
    code = blocks.TextBlock()

    class Meta:
        template = 'code_snippet_block.html'

