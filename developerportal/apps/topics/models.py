# pylint: disable=no-member

from django.db.models import CASCADE, DateField, ForeignKey, SET_NULL
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page

from modelcluster.fields import ParentalKey

from ..articles.models import Article


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

    intro = RichTextField(default='')

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
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

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_articles()
        context['featured'] = self.get_featured_articles()
        return context

    def get_articles(self, limit=12):
        return Article.objects.filter(topics__topic__pk=self.pk).live().public().order_by('-date')[:limit]

    def get_featured_articles(self):
        return [{
            'title': item.article.title,
            'intro': item.article.intro,
            'url': item.article.url,
            'header_image': item.article.header_image
         } for item in self.featured_articles.get_object_list()]


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

    def get_context(self, request):
        context = super().get_context(request)
        context['topics'] = self.get_topics()
        return context

    def get_topics(self, limit=12):
        return Topic.objects.live().public().order_by('title')[:limit]
