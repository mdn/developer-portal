from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.models import Page

from developerportal.apps.common.fields import CustomStreamField


class Article(Page):
    template = 'article.html'

    body = CustomStreamField()

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
