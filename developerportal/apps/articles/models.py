import datetime

from django.forms import CheckboxSelectMultiple
from django.db import models

from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    PageChooserPanel
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.fields import CustomStreamField


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('Article', on_delete=models.CASCADE, related_name='tagged_items')


class Article(Page):
    parent_page_types = ['Articles']
    subpage_types = []
    template = 'article.html'

    # Fields
    intro = RichTextField(default='')
    date = models.DateField('Article date', default=datetime.date.today)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = CustomStreamField()
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)
    labels = ParentalManyToManyField(
        'topics.Topic',
        blank=True,
        related_name='+',
    )

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('date'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body'),
        FieldPanel('labels', widget=CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['related_articles'] = self.get_related(limit=3)
        return context

    def get_related(self, limit=10):
        """Returns live (i.e. not draft), public pages, which are not the current page, ordered by most recent."""
        return Article.objects.live().public().not_page(self).order_by('-date')[:limit]


class Articles(Page):
    subpage_types = ['Article']
    template = 'articles.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_articles(limit=10)
        return context

    def get_articles(self, limit=10):
        """Returns live (i.e. not draft), public pages, ordered by most recent."""
        return Article.objects.live().public().order_by('-date')[:limit]
