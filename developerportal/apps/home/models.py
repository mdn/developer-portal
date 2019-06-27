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
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey

from ..topics.models import Topics


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
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
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
