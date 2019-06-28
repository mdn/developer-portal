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
    intro = TextField(max_length=250, blank=True, default='')
    button_text = CharField(max_length=30, default='')
    button_url = URLField(max_length=140, default='')
    header_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    # featured = StreamField([
    #     StreamBlock([
    #         ('article', PageChooserBlock(required=False, target_model='article')),
    #         ('external', FeaturedExternalBlock())
    #     ], min_num=1, max_num=4)
    # ])
    featured = StreamField(
        StreamBlock([
            ('article', PageChooserBlock(required=False, target_model='articles.article')),
            ('external_page', FeaturedExternalBlock()),
        ], max_num=4),
        null=True,
        blank=True,
    )

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        MultiFieldPanel(
          [
            FieldPanel('button_text'),
            FieldPanel('button_url'),
          ],
          heading="Primary CTA",
        ),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('featured'),
    ]

    featured_panels = [
        MultiFieldPanel([
            InlinePanel('featured_articles', max_num=4),
        ], heading='Featured Articles', help_text=(
            'These articles will appear at the top of the homepage. Please '
            'choose four articles.'
        )),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(featured_panels, heading='Featured'),
        ObjectList(Page.promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def primary_topics(self):
        """The site’s primary topics, i.e. of class Topic but not SubTopic."""
        return Topics.objects.first().get_children().live().public().order_by('title')
