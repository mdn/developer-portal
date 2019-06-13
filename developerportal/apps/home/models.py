from django.db.models import CASCADE, CharField, ForeignKey, SET_NULL, URLField

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

from modelcluster.fields import ParentalKey

from ..topics.models import Topic


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
    subtitle = CharField(max_length=140, default='')
    intro = RichTextField(default='')
    button_text = CharField(max_length=30, default='')
    button_url = URLField(max_length=140, default='')

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
        )
    ]

    featured_panels = [
        MultiFieldPanel([
            InlinePanel('featured_articles', max_num=4),
        ], heading='Featured Articles', help_text=(
            'These articles will appear at the top of the topic page. Please '
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
    def topics(self):
        return Topic.objects.live().public().order_by('title')
