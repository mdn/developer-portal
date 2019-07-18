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
from wagtail.core.fields import RichTextField, StreamField, StreamBlock
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
    subpage_types = ['content.ContentPage']
    template = 'home.html'

    # Content fields
    subtitle = TextField(max_length=250, blank=True, default='')
    button_text = CharField(max_length=30, blank=True, default='')
    button_url = URLField(max_length=2048, blank=True, default='')
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(required=False, target_model=(
                'articles.Article',
                'externalcontent.ExternalArticle',
            ))),
            ('external_page', FeaturedExternalBlock()),
        ], min_num=0, max_num=4),
        null=True,
        blank=True,
    )
    about_title = TextField(max_length=250, blank=True, default='')
    about_subtitle = TextField(max_length=250, blank=True, default='')
    about_button_text = CharField(max_length=30, blank=True, default='')
    about_button_url = URLField(max_length=140, blank=True, default='')

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
    keywords = ClusterTaggableManager(through=HomePageTag, blank=True)

    # Editor panel configuration
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('subtitle'),
                FieldPanel('button_text'),
                FieldPanel('button_url'),
            ],
            heading="Header section",
        ),
        ImageChooserPanel('image'),
        StreamFieldPanel('featured'),
        MultiFieldPanel(
            [
                FieldPanel('about_title'),
                FieldPanel('about_subtitle'),
                FieldPanel('about_button_text'),
                FieldPanel('about_button_url'),
            ],
            heading="About section",
        )
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
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
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

    @property
    def primary_topics(self):
        """The site’s top-level topics, i.e. topics without a parent topic."""
        from ..topics.models import Topic
        return Topic.objects.filter(parent_topics__isnull=True).live().public().order_by('title')
