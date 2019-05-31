from django.db.models import CharField, URLField
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
    PageChooserPanel,
)

class HomePage(Page):
    subpage_types = []
    template = 'home.html'

    # Fields
    subtitle = CharField(max_length=140, default='')
    intro = RichTextField(default='')
    button_text = CharField(max_length=30, default='')
    button_url = URLField(max_length=140, default='')
    
    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        MultiFieldPanel(
          [
            FieldPanel('button_text'),
            FieldPanel('button_url'),
          ],
          heading="Primary CTA",
        )
    ]

    def get_context(self, request):
        context = super().get_context(request)
        return context
