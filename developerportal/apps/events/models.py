# pylint: disable=no-member
import datetime

from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    FloatField,
    ForeignKey,
    SET_NULL,
    TextField,
    URLField,
)

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField, StreamBlock
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    StreamFieldPanel,
)

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.fields import CustomStreamField
from ..common.blocks import AgendaItemBlock, ExternalSpeakerBlock
from ..articles.models import Article


class EventTag(TaggedItemBase):
    content_object = ParentalKey('Event', on_delete=CASCADE, related_name='tagged_items')


class EventTopic(Orderable):
    event = ParentalKey('Event', related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='+')
    panels = [
        PageChooserPanel('topic'),
    ]


class EventSpeaker(Orderable):
    event = ParentalKey('Event', related_name='speaker')
    speaker = ForeignKey('people.Person', on_delete=CASCADE, related_name='+')
    panels = [
        PageChooserPanel('speaker')
    ]


class Events(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['events.Event']
    template = 'events.html'

    # Content fields
    featured_event = ForeignKey('events.Event', blank=True, null=True, on_delete=SET_NULL, related_name='+')

    # Content panels
    content_panels = Page.content_panels + [
        PageChooserPanel('featured_event')
    ]

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
        ObjectList(content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'Events'

    def get_context(self, request):
        context = super().get_context(request)
        context['filters'] = self.get_filters()
        return context

    @property
    def events(self):
        """Return events in chronological order"""
        return (
            Event
                .objects
                .all()
                .public()
                .live()
                .order_by('start_date')
        )

    def get_filters(self):
        from ..topics.models import Topic
        return {
            'months': True,
            'topics': Topic.objects.live().public().order_by('title'),
        }


class Event(Page):
    resource_type = 'event'
    parent_page_types = ['events.Events']
    subpage_types = []
    template = 'event.html'

    # Content fields
    description = TextField(max_length=250, blank=True, default='')
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    body = CustomStreamField(blank=True, null=True)
    agenda = StreamField(
        StreamBlock([
            ('agenda_item', AgendaItemBlock()),
        ], required=False),
        blank=True, null=True
    )
    speakers = StreamField(
        StreamBlock([
            ('speaker', PageChooserBlock(required=False, target_model='people.Person')),
            ('external_speaker', ExternalSpeakerBlock(required=False)),
        ], required=False),
        blank=True, null=True
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

    # Meta fields
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    venue = TextField(max_length=250, blank=True, default='', help_text='Full address of the event venue, displayed on the event detail page')
    location = CharField(max_length=100, blank=True, default='', help_text='Location details (city and country), displayed on event cards')
    latitude = FloatField(blank=True, null=True)
    longitude = FloatField(blank=True, null=True)
    register_url = URLField('Register URL', blank=True, null=True)
    keywords = ClusterTaggableManager(through=EventTag, blank=True)

    # Content panels
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        StreamFieldPanel('agenda'),
        StreamFieldPanel('speakers'),
    ]

    # Card panels
    card_panels = [
        FieldPanel('card_title'),
        FieldPanel('card_description'),
        ImageChooserPanel('card_image'),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
            FieldPanel('venue'),
            FieldPanel('location'),
            FieldPanel('latitude'),
            FieldPanel('longitude'),
            FieldPanel('register_url'),
        ], heading='Event details'),
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics', help_text=(
            'These are the topic pages the article will appear on. The first '
            'topic in the list will be treated as the primary topic.'
        )),
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
        ObjectList(content_panels, heading='Content'),
        ObjectList(card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the event."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None

    @property
    def month_group(self):
        return self.start_date.replace(day=1)

    @property
    def event_dates(self):
        """Return a formatted string of the event start and end dates"""
        event_dates = self.start_date.strftime("%b %-d")
        if self.end_date:
            event_dates += " &ndash; "
            start_month = self.start_date.strftime("%m")
            if self.end_date.strftime("%m") == start_month:
                event_dates += self.end_date.strftime("%-d")
            else:
                event_dates += self.end_date.strftime("%b %-d")
        return event_dates

    @property
    def event_dates_full(self):
        """Return a formatted string of the event start and end dates, including the year"""
        return self.event_dates + self.start_date.strftime(", %Y")
