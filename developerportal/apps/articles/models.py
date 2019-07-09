import datetime
import readtime

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import CASCADE, DateField, ForeignKey, SET_NULL, TextField
from django.forms import CheckboxSelectMultiple

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.fields import CustomStreamField


class Articles(Page):
    subpage_types = ['Article']
    template = 'articles.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['filters'] = self.get_filters()
        return context

    @property
    def articles(self):
        return Article.objects.all().public().live().order_by('-date')

    def get_filters(self):
        return {
            'months': True,
            'topics': apps.get_model('topics', 'Topic').objects.live().public().order_by('title'),
        }


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('Article', on_delete=CASCADE, related_name='tagged_items')


class ArticleTopic(Orderable):
    article = ParentalKey('Article', related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('topic'),
    ]


class ArticleAuthor(Orderable):
    article = ParentalKey('Article', related_name='authors')
    author = ForeignKey('people.Person', on_delete=CASCADE, related_name='articles')

    panels = [
        PageChooserPanel('author')
    ]


class Article(Page):
    resource_type = 'article'
    parent_page_types = ['Articles']
    subpage_types = []
    template = 'article.html'

    # Fields
    intro = TextField(max_length=250, blank=True, default='')
    date = DateField('Article date', default=datetime.date.today)
    header_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    body = CustomStreamField()
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            InlinePanel('authors'),
        ], heading='Authors'),
        FieldPanel('date'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body'),
    ]

    topic_panels = [
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics', help_text=(
            'These are the topic pages the article will appear on. The first '
            'topic in the list will be treated as the primary topic.'
        )),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(topic_panels, heading='Topics'),
        ObjectList(promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the article."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None

    @property
    def read_time(self):
        return str(readtime.of_html(str(self.body)))

    @property
    def related_articles(self):
        """Returns articles that are related to the current article, i.e. live, public articles which have the same
        topic, but are not the current article."""
        topic_pks = self.topics.values_list('topic')
        return (
            Article
            .objects
            .filter(topics__topic__pk__in=topic_pks)
            .not_page(self)
            .distinct()
            .live()
            .public()
        )

    @property
    def month_group(self):
        return self.date.replace(day=1)
