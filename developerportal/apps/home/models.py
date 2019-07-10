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


class HomePage(Page):
    subpage_types = []
    template = 'home.html'

    # Fields
    subtitle = TextField(max_length=250, blank=True, default='')
    intro = TextField(max_length=250, blank=True, default='')
    button_text = CharField(max_length=30, blank=True, default='')
    button_url = URLField(max_length=2048, blank=True, default='')
    header_image = ForeignKey(
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

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def primary_topics(self):
        """The site’s primary topics, i.e. of class Topic but not SubTopic."""
        topic = Topics.objects.first()
        return topic.get_children().live().public().order_by('title') if topic else None
