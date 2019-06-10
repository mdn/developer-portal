# pylint: disable=no-member

from django.db.models import CASCADE, DateField, ForeignKey, SET_NULL
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import (
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.models import Orderable, Page

from modelcluster.fields import ParentalKey

from ..articles.models import Article


class TopicFeaturedArticle(Orderable):
    topic = ParentalKey('Topic', related_name='featured_articles')
    article = ForeignKey('articles.Article', null=True, blank=False, on_delete=CASCADE)

    panels = [
        PageChooserPanel('article'),
    ]


class Topic(Page):
    parent_page_types = ['Topics']
    subpage_types = ['SubTopic']
    template = 'topic.html'

    featured_panels = [
        MultiFieldPanel([
            InlinePanel('featured_articles', min_num=4, max_num=4)
        ], heading='Featured Articles', help_text=(
            'These articles will appear at the top of the topic page. Please '
            'choose four articles.'
        )),
    ]

    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Content'),
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
            'description': item.article.search_description,
            'url': item.article.url,
         } for item in self.featured_articles.get_object_list()]


class SubTopic(Topic):
    parent_page_types = ['Topic']
    subpage_types = []
    template = 'topic.html'

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
