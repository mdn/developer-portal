import datetime
import readtime

from django.forms import CheckboxSelectMultiple
from django.db.models import CASCADE, DateField, ForeignKey, SET_NULL

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from ..common.fields import CustomStreamField


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey('Article', on_delete=CASCADE, related_name='tagged_items')


class ArticleTopic(Orderable):
    article = ParentalKey('Article', related_name='topics')
    topic = ForeignKey('topics.Topic', null=True, blank=False, on_delete=CASCADE)

    panels = [
        PageChooserPanel('topic'),
    ]


class Article(Page):
    parent_page_types = ['Articles']
    subpage_types = []
    template = 'article.html'

    # Fields
    intro = RichTextField(default='')
    author = ForeignKey(
      'wagtailcore.Page',
      null=True,
      blank=True,
      on_delete=SET_NULL,
      related_name='+',
    )
    date = DateField('Article date', default=datetime.date.today)
    header_image = ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    body = CustomStreamField()
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)

    # Editor panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        PageChooserPanel('author', 'people.person'),
        FieldPanel('date'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body'),
    ]

    topic_panels = [
        MultiFieldPanel([
            InlinePanel('topics', min_num=1)
        ], heading='Topics', help_text=(
            'These are the topic pages the article will appear on. The first '
            'topic in the list will be treated as the primary topic.'
        )),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(topic_panels, heading='Topics'),
        ObjectList(promote_panels, heading='SEO'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    def get_context(self, request):
        context = super().get_context(request)
        context['related_articles'] = self.get_related(limit=3)
        context['read_time'] = str(readtime.of_html(str(self.body)))
        return context

    def get_related(self, limit=12):
        """Returns articles that are related to the current article, i.e. live, public articles which have the same
        topic, but are not the current article."""
        topic_ids = [topic.id for topic in self.topics.get_object_list()]  # pylint: disable=no-member
        return (
            Article
            .objects
            .all()
            .live()
            .public()
            .not_page(self)
            .order_by('-date')
            .filter(topics__in=topic_ids)[:limit]
        )


class Articles(Page):
    subpage_types = ['Article']
    template = 'articles.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_articles(limit=10)
        return context

    def get_articles(self, limit=10):
        """Returns live (i.e. not draft), public pages, ordered by most recent."""
        return Article.objects.live().public().order_by('-date')[:limit]
