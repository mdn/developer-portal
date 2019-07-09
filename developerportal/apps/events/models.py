import datetime

from django.db.models import TextField, DateField, URLField, ForeignKey, CASCADE, SET_NULL, FloatField

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField, StreamBlock
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel, TabbedInterface, ObjectList

from modelcluster.fields import ParentalKey

from ..common.fields import CustomStreamField
from ..common.blocks import AgendaItemBlock, ExternalSpeakerBlock
from ..articles.models import Article


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


class Event(Page):
    resource_type = 'event'
    parent_page_types = ['events.Events']
    subpage_types = []
    template = 'event.html'

    # Fields
    description = TextField(max_length=250, blank=True, default='')
    header_image = ForeignKey('mozimages.MozImage', blank=True, null=True, on_delete=SET_NULL, related_name='+')
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    venue = TextField(max_length=250, blank=True, default='')
    latitude = FloatField(blank=True, null=True)
    longitude = FloatField(blank=True, null=True)
    register_url = URLField('Register URL', blank=True, null=True)
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

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('header_image'),
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
            FieldPanel('venue'),
            FieldPanel('latitude'),
            FieldPanel('longitude'),
            FieldPanel('register_url'),
        ], heading='Event details'),
        StreamFieldPanel('body'),
        StreamFieldPanel('agenda'),
        StreamFieldPanel('speakers'),
    ]

    topic_panels = [
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics', help_text=(
            'These are the topic pages the event will appear on. The first '
            'topic in the list will be treated as the primary topic.'
        )),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(topic_panels, heading='Topics'),
        ObjectList(Page.promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        ordering = ['-start_date']

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the event."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None


class Events(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['events.Event']
    template = 'events.html'

    @property
    def events(self):
        """Return live public event pages, most recent first. """
        return Event.objects.live().public()
