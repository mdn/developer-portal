import datetime

from django.db.models import TextField, DateField, URLField, ForeignKey, CASCADE

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField, StreamBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel

from modelcluster.fields import ParentalKey

from ..common.fields import CustomStreamField
from ..common.blocks import AgendaItemBlock


class EventSpeaker(Orderable):
    event = ParentalKey('Event', related_name='speaker')
    speaker = ForeignKey('people.Person', on_delete=CASCADE, related_name='+')
    panels = [
        PageChooserPanel('person')
    ]

class Event(Page):
    subpage_types = []
    template = 'event.html'

    # Fields
    intro = TextField(max_length=250, blank=True, default='')
    date = DateField('Event start date', default=datetime.date.today)
    end_date = DateField('Event end date', required=False)
    address = TextField(max_length=250, blank=True, default='')
    register_url = URLField()
    body = CustomStreamField()
    register_url = URLField()
    agenda = StreamField(
        StreamBlock([
            ('agenda_item', AgendaItemBlock())
        ])
    )

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        ImageChooserPanel('header_image'),
        FieldPanel('date'),
        FieldPanel('end_date'),
        FieldPanel('address'),
        FieldPanel('register_url'),
        StreamFieldPanel('body'),
        StreamFieldPanel('agenda'),
        MultiFieldPanel([
            InlinePanel('speaker'),
        ], heading='Speakers'),
    ]
