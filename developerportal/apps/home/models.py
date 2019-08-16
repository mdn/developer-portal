from django.db.models import CASCADE, CharField, ForeignKey, SET_NULL, URLField, TextField

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import StreamField, StreamBlock
from wagtail.core.models import Orderable, Page
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.blocks import FeaturedExternalBlock


class HomePageTag(TaggedItemBase):
    content_object = ParentalKey('HomePage', on_delete=CASCADE, related_name='tagged_items')


class HomePage(Page):
    subpage_types = [
        'articles.Articles',
        'content.ContentPage',
        'events.Events',
        'people.People',
        'topics.Topics',
        'videos.Videos',
    ]
    template = 'home.html'

    # Content fields
    subtitle = TextField(max_length=250, blank=True, default='')
    button_text = CharField(max_length=30, blank=True, default='')
    button_url = CharField(max_length=2048, blank=True, default='')
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    external_promos = StreamField(
        StreamBlock([
            ('external_promo', FeaturedExternalBlock()),
        ], max_num=2, required=False),
        null=True,
        blank=True,
        help_text='Optional promo space under the header for linking to external sites, max. 2',
    )
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(target_model=(
                'articles.Article',
                'externalcontent.ExternalArticle',
            ))),
            ('external_page', FeaturedExternalBlock()),
        ], max_num=4, required=False),
        null=True,
        blank=True,
        help_text='Optional space for featured articles, max. 4',
    )
    about_title = TextField(max_length=250, blank=True, default='')
    about_subtitle = TextField(max_length=250, blank=True, default='')
    about_button_text = CharField(max_length=30, blank=True, default='')
    about_button_url = URLField(max_length=140, blank=True, default='')

    # Card fields
    card_title = CharField('Title', max_length=140, blank=True, default='')
    card_description = TextField('Description', max_length=400, blank=True, default='')
    card_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+',
        verbose_name='Image',
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=HomePageTag, blank=True)

    # Editor panel configuration
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('subtitle'),
            FieldPanel('button_text'),
            FieldPanel('button_url'),
        ], heading='Header section', help_text='Optional fields for the header section'),
        MultiFieldPanel([
            ImageChooserPanel('image'),
        ], heading='Image', help_text='Optional image shown when sharing this page through social media'),
        StreamFieldPanel('external_promos'),
        StreamFieldPanel('featured'),
        MultiFieldPanel([
            FieldPanel('about_title'),
            FieldPanel('about_subtitle'),
            FieldPanel('about_button_text'),
            FieldPanel('about_button_url'),
        ], heading='About section', help_text='Optional section to explain more about Mozilla'),
    ]

    # Card panels
    card_panels = [
        MultiFieldPanel([
            FieldPanel('card_title'),
            FieldPanel('card_description'),
            ImageChooserPanel('card_image'),
        ], heading='Card overrides', help_text=(
            'Optional fields to override the default title, description and image when this page is shown as a card'
        )),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO', help_text='Optional fields to override the default title and description for SEO purposes'),
    ]

    # Settings panels
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

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    @property
    def primary_topics(self):
        """The site’s top-level topics, i.e. topics without a parent topic."""
        from ..topics.models import Topic
        return Topic.objects.filter(parent_topics__isnull=True).live().public().order_by('title')
