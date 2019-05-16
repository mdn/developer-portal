import datetime
from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

class Article(Page):
    template = 'article.html'

    # Fields
    intro = RichTextField("Intro", default='')
    date = models.DateField("Article date", default=datetime.date.today)

    # Editor panel configuration
    content_panels = Page.content_panels + [
      FieldPanel('intro'),
      FieldPanel('date')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # published pages
        # not the current page
        # most recent first
        # up to 3
        articles = Article.objects.all().live().not_page(self).order_by('-date')[:3]
        context['articles'] = articles
        return context
