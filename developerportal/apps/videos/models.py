import datetime
import readtime

from django.db.models import CASCADE, CharField, DateField, ForeignKey, SET_NULL, TextField

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField, StreamField, StreamBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.core.blocks import PageChooserBlock


from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.constants import VIDEO_TYPE


class VideosTag(TaggedItemBase):
    content_object = ParentalKey('Videos', on_delete=CASCADE, related_name='tagged_items')


class VideoTopic(Orderable):
    video = ParentalKey('Video', related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('topic'),
    ]


class Videos(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['Video']
    template = 'videos.html'

    # Meta fields
    keywords = ClusterTaggableManager(through=VideosTag, blank=True)

    meta_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    settings_panels = [
        FieldPanel('slug'),
        FieldPanel('show_in_menus'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'Videos'

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    @property
    def videos(self):
        return Video.objects.live().public().order_by('title')


class VideoTag(TaggedItemBase):
    content_object = ParentalKey('Video', on_delete=CASCADE, related_name='tagged_items')


class Video(Page):
    resource_type = 'video'
    parent_page_types = ['Videos']
    subpage_types = []
    template = 'video.html'

    # Content fields
    body = RichTextField(default='', blank=True)
    description = CharField(default='', blank=True, max_length=250)
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    types = CharField(max_length=14, choices=VIDEO_TYPE, default='conference')
    duration = CharField(max_length=30, blank=True, null=True, help_text=(
        'Optional. Video duration in MM:SS format e.g. “12:34”. Shown as a small hint when the video is displayed as a card.'
    ))
    transcript = RichTextField(default='', blank=True)
    video_url = StreamField(
        StreamBlock([
            ('embed', EmbedBlock()),
        ], max_num=1),
        null=True,
        blank=True,
    )
    speakers = StreamField(
        StreamBlock([
            ('speaker', PageChooserBlock(required=False, target_model='people.Person')),
        ], required=False),
        blank=True, null=True,
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
    date = DateField('Upload date', default=datetime.date.today)
    keywords = ClusterTaggableManager(through=VideoTag, blank=True)

    # Content panels
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
        StreamFieldPanel('video_url'),
        FieldPanel('body'),
        FieldPanel('transcript'),
    ]

    # Card panels
    card_panels = [
        FieldPanel('card_title'),
        FieldPanel('card_description'),
        ImageChooserPanel('card_image'),
    ]

    # Meta panels
    meta_panels = [
        FieldPanel('date'),
        StreamFieldPanel('speakers'),
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics'),
        FieldPanel('duration'),
        MultiFieldPanel([
            FieldPanel('types'),
        ], heading='Type.'),


        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]

    # Tabs
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    def has_speaker(self, person):
        for speaker in self.speakers:
            if str(speaker.value)==str(person.title):
                return True
        return False
