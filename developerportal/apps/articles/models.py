import datetime

from django.forms import CheckboxSelectMultiple
from django.db.models import CASCADE, DateField

from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    PageChooserPanel,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.fields import CustomStreamField


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('Article', on_delete=CASCADE, related_name='tagged_items')


class Article(Page):
    parent_page_types = ['Articles']
    subpage_types = []
    template = 'article.html'

    # Fields
    intro = RichTextField(default='')
    date = DateField('Article date', default=datetime.date.today)
    body = CustomStreamField()
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)
    topics = ParentalManyToManyField(
        'topics.Topic',
        blank=True,
        related_name='+',
    )

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
        FieldPanel('topics', widget=CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['related_articles'] = self.get_related(limit=3)
        return context

    def get_related(self, limit=12):
        """Returns articles that are related to the current article, i.e. live, public articles which have the same
        topic, but are not the current article."""
        topic_ids = [topic.id for topic in self.topics.get_object_list()]  # pylint: disable=no-member
        return (
            Article
            .objects
            .all()
            .live()
            .public()
            .not_page(self)
            .order_by('-date')
            .filter(topics__in=topic_ids)[:limit]
        )


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
