# pylint: disable=no-member
import datetime
from itertools import chain
from operator import attrgetter
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
from wagtail.core.fields import StreamField, StreamBlock
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.blocks import ExternalAuthorBlock, ExternalLinkBlock
from ..common.fields import CustomStreamField
from ..common.utils import get_combined_articles, get_combined_articles_and_videos


class ArticlesTag(TaggedItemBase):
    content_object = ParentalKey('Articles', on_delete=CASCADE, related_name='tagged_items')


class Articles(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['Article']
    template = 'articles.html'

    # Content fields
    description = TextField(
        blank=True,
        default='',
        help_text='Optional short text description, max. 250 characters',
        max_length=250,
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=ArticlesTag, blank=True)

    # Content panels
    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO', help_text=(
            'Optional fields to override the default title and description for SEO purposes'
        )),
    ]

    # Settings panels
    settings_panels = [
        FieldPanel('slug'),
        FieldPanel('show_in_menus'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'Articles'

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    def get_context(self, request):
        context = super().get_context(request)
        context['filters'] = self.get_filters()
        return context

    @property
    def articles(self):
        return get_combined_articles(self)

    def get_filters(self):
        from ..topics.models import Topic
        return {
            'months': True,
            'topics': Topic.objects.live().public().order_by('title'),
        }


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('Article', on_delete=CASCADE, related_name='tagged_items')


class ArticleTopic(Orderable):
    article = ParentalKey('Article', related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('topic'),
    ]


class Article(Page):
    resource_type = 'article'
    parent_page_types = ['Articles']
    subpage_types = []
    template = 'article.html'

    # Content fields
    description = TextField(
        blank=True,
        default='',
        help_text='Optional short text description, max. 250 characters',
        max_length=250,
    )
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+',
    )
    body = CustomStreamField()
    related_links_mdn = StreamField(
        StreamBlock([
            ('link', ExternalLinkBlock())
        ], required=False),
        blank=True,
        null=True,
        help_text='Optional links to MDN Web Docs for further reading',
        verbose_name='Related MDN links',
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
    date = DateField('Article date', default=datetime.date.today, help_text='The date the article was published')
    authors = StreamField(
        StreamBlock([
            ('author', PageChooserBlock(target_model='people.Person')),
            ('external_author', ExternalAuthorBlock()),
        ]),
        blank=True,
        null=True,
        help_text=(
            'Optional list of the article’s authors. Use ‘External author’ to add guest authors without creating a '
            'profile on the system'
        )
    )
    keywords = ClusterTaggableManager(through=ArticleTag, blank=True)

    # Content panels
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        MultiFieldPanel([
            ImageChooserPanel('image'),
        ], heading='Image', help_text='Optional image shown when sharing this page through social media'),
        StreamFieldPanel('body'),
        StreamFieldPanel('related_links_mdn'),
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
        StreamFieldPanel('authors'),
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics', help_text=(
            'The topic pages this article will appear on. The first topic in the list will be treated as the primary '
            'topic'
        )),
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO', help_text=(
            'Optional fields to override the default title and description for SEO purposes'
        )),
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

    # Rss feed
    def get_absolute_url(self):
        return self.full_url

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the article."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None

    @property
    def read_time(self):
        return str(readtime.of_html(str(self.body)))

    @property
    def related_resources(self):
        """Returns resources that are related to the current resource, i.e. live, public articles and videos which
        have the same topics."""
        topic_pks = [topic.topic.pk for topic in self.topics.all()]
        return get_combined_articles_and_videos(self, topics__topic__pk__in=topic_pks)

    @property
    def month_group(self):
        return self.date.replace(day=1)

    def has_author(self, person):
        for author in self.authors:  # pylint: disable=not-an-iterable
            if (author.block_type=='author' and str(author.value) == str(person.title)):
                return True
        return False
