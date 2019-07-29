# pylint: disable=no-member
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
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.blocks import FeaturedExternalBlock, GetStartedBlock
from ..common.constants import COLOR_CHOICES, COLOR_VALUES
from ..common.utils import get_combined_articles, get_combined_events


class TopicsTag(TaggedItemBase):
    content_object = ParentalKey('Topics', on_delete=CASCADE, related_name='tagged_items')


class TopicTag(TaggedItemBase):
    content_object = ParentalKey('Topic', on_delete=CASCADE, related_name='tagged_items')


class TopicPerson(Orderable):
    topic = ParentalKey('Topic', related_name='people')
    person = ForeignKey('people.Person', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('person'),
    ]


class ParentTopic(Orderable):
    child = ParentalKey('Topic', related_name='parent_topics')
    parent = ParentalKey('Topic', on_delete=CASCADE, related_name='child_topics')

    panels = [
        PageChooserPanel('child'),
        PageChooserPanel('parent'),
    ]


class Topic(Page):
    resource_type = 'topic'
    parent_page_types = ['Topics']
    subpage_types = ['Topic']
    template = 'topic.html'

    # Content fields
    description = TextField(max_length=250, blank=True, default='')
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(required=False, target_model=(
                'articles.Article',
                'externalcontent.ExternalArticle',
            ))),
            ('external_page', FeaturedExternalBlock()),
        ], min_num=0, max_num=4, required=False),
        null=True,
        blank=True,
    )
    get_started = StreamField(
        StreamBlock([
            ('panel', GetStartedBlock())
        ], min_num=0, max_num=3, required=False),
        null=True,
        blank=True,
    )

    # Card fields
    card_title = CharField('Title', max_length=140, blank=True, default='')
    card_description = TextField('Description', max_length=140, blank=True, default='')
    card_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+',
        verbose_name='Image',
    )

    # Meta
    icon = FileField(upload_to='topics/icons', blank=True, default='')
    color = CharField(max_length=14, choices=COLOR_CHOICES, default='blue-40')
    keywords = ClusterTaggableManager(through=TopicTag, blank=True)

    # Content panels
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        StreamFieldPanel('featured'),
        StreamFieldPanel('get_started'),
        MultiFieldPanel([
            InlinePanel('people'),
        ], heading='People'),
    ]

    # Card panels
    card_panels = [
        FieldPanel('card_title'),
        FieldPanel('card_description'),
        ImageChooserPanel('card_image'),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel(
            [
                InlinePanel('parent_topics', label='Parent topic(s)'),
                InlinePanel('child_topics', label='Child topic(s)'),
            ],
            heading='Parent/child topic(s)',
            classname='collapsible collapsed',
            help_text=(
                'Topics with no parent (i.e. top-level topics) will be listed '
                'on the home page. Child topics are listed on the parent '
                'topic’s page.'
            )
        ),
        MultiFieldPanel([
            FieldPanel('icon'),
            FieldPanel('color'),
        ], heading='Theme'),
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    # Settings panels
    settings_panels = [
        FieldPanel('slug'),
        FieldPanel('show_in_menus'),
    ]

    # Tabs
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def articles(self):
        return get_combined_articles(self, topics__topic__pk=self.pk)

    @property
    def events(self):
        """Return upcoming events for this topic,
        ignoring events in the past, ordered by start date"""
        return get_combined_events(self, topics__topic__pk=self.pk, start_date__gte=datetime.datetime.now())

    @property
    def color_value(self):
        return dict(COLOR_VALUES)[self.color]

    @property
    def subtopics(self):
        return [topic.child for topic in self.child_topics.all()]


class Topics(Page):
    subpage_types = ['Topic']
    template = 'topics.html'

    # Meta fields
    keywords = ClusterTaggableManager(through=TopicsTag, blank=True)

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    # Settings panels
    settings_panels = [
        FieldPanel('slug'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'Topics'

    @property
    def topics(self):
        return Topic.objects.live().public().order_by('title')
