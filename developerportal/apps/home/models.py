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

from ..topics.models import Topics, Topic
from ..common.blocks import FeaturedExternalBlock


class HomePageFeaturedArticle(Orderable):
    page = ParentalKey('HomePage', related_name='featured_articles')
    article = ForeignKey('articles.Article', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('article'),
    ]


class HomePage(Page):
    subpage_types = []
    template = 'home.html'

    # Fields
    subtitle = TextField(max_length=250, blank=True, default='')
    button_text = CharField(max_length=30, blank=True, default='')
    button_url = URLField(max_length=140, blank=True, default='')
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(required=False, target_model='articles.article')),
            ('external_page', FeaturedExternalBlock()),
        ], max_num=4),
        null=True,
        blank=True,
    )
    about_title = TextField(max_length=250, blank=True, default='')
    about_subtitle = TextField(max_length=250, blank=True, default='')
    about_button_text = CharField(max_length=30, blank=True, default='')
    about_button_url = URLField(max_length=140, blank=True, default='')

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

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def primary_topics(self):
        """The site’s primary topics, i.e. of class Topic but not SubTopic."""
        return Topics.objects.first().get_children().live().public().order_by('title')
