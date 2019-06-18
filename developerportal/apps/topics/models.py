from django.db.models import CASCADE, CharField, DateField, ForeignKey, SET_NULL, TextField
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    StreamFieldPanel,
)
from wagtail.core.models import Orderable, Page

from modelcluster.fields import ParentalKey
from wagtail.core.fields import StreamField, StreamBlock

from ..articles.models import Article
from ..common.constants import COLOR_CHOICES, COLOR_VALUES
from ..common.blocks import GetStartedBlock

class TopicFeaturedArticle(Orderable):
    topic = ParentalKey('Topic', related_name='featured_articles')
    article = ForeignKey('articles.Article', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('article'),
    ]


class TopicPerson(Orderable):
    topic = ParentalKey('Topic', related_name='people')
    person = ForeignKey('people.Person', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('person'),
    ]


class Topic(Page):
    parent_page_types = ['Topics']
    subpage_types = ['SubTopic']
    template = 'topic.html'
    show_in_menus_default = True

    intro = TextField(max_length=250, blank=True, default='')
    color = CharField(max_length=14, choices=COLOR_CHOICES, default='blue')
    get_started = StreamField(
        StreamBlock([
            ('panel', GetStartedBlock())
        ], min_num=1, max_num=3)
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('color'),
        StreamFieldPanel('get_started'),
        MultiFieldPanel([
            InlinePanel('people'),
        ], heading='Meet the Mozillians'),
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
    def articles(self):
        return Article.objects.filter(topics__topic__pk=self.pk).live().public()

    @property
    def color_value(self):
        return dict(COLOR_VALUES)[self.color]


class SubTopic(Topic):
    parent_page_types = ['Topic']
    subpage_types = []
    template = 'topic.html'
    show_in_menus_default = False

    class Meta:
        verbose_name = _('Sub-topic')
        verbose_name_plural = _('Sub-topics')


class Topics(Page):
    subpage_types = ['Topic']
    template = 'topics.html'

    @property
    def topics(self):
        return Topic.objects.live().public().order_by('title')
