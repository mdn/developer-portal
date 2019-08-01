import datetime

from django.db.models import CASCADE, CharField, DateField, ForeignKey, SET_NULL, TextField, URLField

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import StreamField, StreamBlock
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel


class ExternalContent(Page):
    is_external = True
    subpage_types = []

    # Card fields
    description = TextField(max_length=250, blank=True, default='')
    external_url = URLField('URL', max_length=2048, blank=True, default='')
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )

    card_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
        FieldPanel('external_url'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(card_panels, heading='Card'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'External Content'

    def get_full_url(self, request=None):
        return self.external_url

    def get_url(self, request=None, current_site=None):
        return self.external_url

    def relative_url(self, current_site, request=None):
        return self.external_url

    @property
    def url(self):
        return self.external_url


class ExternalArticleTopic(Orderable):
    article = ParentalKey('ExternalArticle', on_delete=CASCADE, related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='external_articles')

    panels = [
        PageChooserPanel('topic')
    ]


class ExternalArticle(ExternalContent):
    resource_type = 'article'

    date = DateField('Article date', default=datetime.date.today)
    read_time = CharField(max_length=30, blank=True, help_text=(
        'Optional, approximate read-time for this article, e.g. “2 mins”. This '
        'is shown as a small hint when the article is displayed as a card.'
    ))

    meta_panels = [
        FieldPanel('date'),
        StreamFieldPanel('authors'),
        InlinePanel('topics', heading='Topics'),
        FieldPanel('read_time'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(ExternalContent.card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def article(self):
        return self

    @property
    def month_group(self):
        return self.date.replace(day=1)

    def has_author(self, person):
        for author in self.authors:
            if (author.block_type=='author' and str(author.value)==str(person.title)):
                return True
        return False

class ExternalEventTopic(Orderable):
    event = ParentalKey('ExternalEvent', on_delete=CASCADE, related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='external_events')

    panels = [
        PageChooserPanel('topic')
    ]


class ExternalEventSpeaker(Orderable):
    article = ParentalKey('ExternalEvent', on_delete=CASCADE, related_name='speakers')
    speaker = ForeignKey('people.Person', on_delete=CASCADE, related_name='external_events')

    panels = [
        PageChooserPanel('speaker')
    ]


class ExternalEvent(ExternalContent):
    resource_type = 'event'

    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    venue = TextField(max_length=250, blank=True, default='', help_text='Full address of the event venue, displayed on the event detail page')
    location = CharField(max_length=100, blank=True, default='', help_text='Location details (city and country), displayed on event cards')

    meta_panels = [
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
            FieldPanel('venue'),
            FieldPanel('location'),
        ], heading='Event details'),
        InlinePanel('topics', heading='Topics'),
        InlinePanel('speakers', heading='Speakers'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(ExternalContent.card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def event(self):
        return self

    @property
    def month_group(self):
        return self.date.replace(day=1)


class ExternalVideoTopic(Orderable):
    video = ParentalKey('ExternalVideo', on_delete=CASCADE, related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='external_videos')

    panels = [
        PageChooserPanel('topic')
    ]


class ExternalVideoPerson(Orderable):
    article = ParentalKey('ExternalVideo', on_delete=CASCADE, related_name='people')
    person = ForeignKey('people.Person', on_delete=CASCADE, related_name='external_videos')

    panels = [
        PageChooserPanel('person')
    ]


class ExternalVideo(ExternalContent):
    date = DateField('Video date', default=datetime.date.today)
    video_duration = CharField(max_length=30, blank=True, null=True, help_text=(
        'Optional, duration for this video in MM:SS format e.g. “12:34”. This '
        'is shown as a small hint when the video is displayed as a card.'
    ))

    meta_panels = [
        FieldPanel('date'),
        InlinePanel('topics', heading='Topics'),
        InlinePanel('people', heading='People', help_text=(
            'Optional, people associated with this video.'
        )),
        FieldPanel('video_duration'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(ExternalContent.card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def video(self):
        return self
