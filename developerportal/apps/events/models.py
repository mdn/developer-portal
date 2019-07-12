import datetime

from django.db.models import TextField, DateField, URLField, ForeignKey, CASCADE, SET_NULL, CharField

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


class Events(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['events.Event']
    template = 'events.html'

    # Fields
    featured_event = ForeignKey('events.Event', blank=True, null=True, on_delete=SET_NULL, related_name='+')

    # Editor panel configuration
    content_panels = Page.content_panels + [
        PageChooserPanel('featured_event')
    ]

    class Meta:
        verbose_name_plural = 'Events'

    def get_context(self, request):
        context = super().get_context(request)
        context['filters'] = self.get_filters()
        return context

    @property
    def events(self):
        return Event.objects.all().public().live().order_by('-start_date')

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

    # Fields
    description = TextField(max_length=250, blank=True, default='')
    header_image = ForeignKey('mozimages.MozImage', blank=True, null=True, on_delete=SET_NULL, related_name='+')
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    venue = TextField(max_length=250, blank=True, default='', help_text='Full address of the event venue, displayed on the event detail page')
    card_venue = CharField(max_length=100, blank=True, default='', help_text='Location details (city and country), displayed on event cards')
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
            FieldPanel('card_venue'),
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

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the event."""
        article_topic = self.topics.first()  # pylint: disable=no-member
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
