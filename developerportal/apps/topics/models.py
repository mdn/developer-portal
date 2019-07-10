import datetime
from django.db.models import CASCADE, CharField, DateField, ForeignKey, SET_NULL, TextField, FileField
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField, StreamBlock
from wagtail.core.models import Orderable, Page
from wagtail.core.blocks import PageChooserBlock

from modelcluster.fields import ParentalKey

from ..articles.models import Article
from ..events.models import Event
from ..common.constants import COLOR_CHOICES, COLOR_VALUES
from ..common.blocks import FeaturedExternalBlock, GetStartedBlock

class TopicFeaturedArticle(Orderable):
    topic = ParentalKey('Topic', related_name='featured_articles')
    article = ForeignKey('articles.Article', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('article'),
    ]


class TopicPerson(Orderable):
    topic = ParentalKey('Topic', related_name='people')
    person = ForeignKey('people.Person', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('person'),
    ]


class Topic(Page):
    resource_type = 'topic'
    parent_page_types = ['Topics']
    subpage_types = ['SubTopic']
    template = 'topic.html'
    show_in_menus_default = True

    intro = TextField(max_length=250, blank=True, default='')
    icon = FileField(upload_to='topics/icons', blank=True, default='')
    color = CharField(max_length=14, choices=COLOR_CHOICES, default='blue-40')
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(required=False, target_model='articles.article')),
            ('external_page', FeaturedExternalBlock()),
        ], max_num=4),
        null=True,
        blank=True,
    )
    get_started = StreamField(
        StreamBlock([
            ('panel', GetStartedBlock())
        ], max_num=3)
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('icon'),
        FieldPanel('color'),
        StreamFieldPanel('featured'),
        StreamFieldPanel('get_started'),
        MultiFieldPanel([
            InlinePanel('people'),
        ], heading='People'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def articles(self):
        return (
            Article
                .objects
                .filter(topics__topic__pk=self.pk)
                .live()
                .public()
                .order_by('-date')
        )

    @property
    def events(self):
        """Return upcoming events for this topic,
        ignoring events in the past, ordered by start date"""
        return (
            Event
                .objects
                .filter(topics__topic__pk=self.pk)
                .filter(start_date__gte=datetime.datetime.now())
                .order_by('start_date')
                .live()
                .public()
        )

    @property
    def color_value(self):
        return dict(COLOR_VALUES)[self.color]


class SubTopic(Topic):
    parent_page_types = ['Topic']
    subpage_types = []
    template = 'topic.html'
    show_in_menus_default = False

    class Meta:
        verbose_name = _('Sub-topic')
        verbose_name_plural = _('Sub-topics')


class Topics(Page):
    subpage_types = ['Topic']
    template = 'topics.html'

    class Meta:
        verbose_name_plural = 'Topics'

    @property
    def topics(self):
        return Topic.objects.live().public().order_by('title')
