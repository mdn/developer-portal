from wagtail.core.models import Page

from ..articles.models import Article


class Topic(Page):
    parent_page_types = ['Topics']
    subpage_types = ['SubTopic']
    template = 'topic.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_articles()
        return context

    def get_articles(self, limit=12):
        return Article.objects.filter(labels__pk=self.pk).live().public().order_by('-date')[:limit]


class SubTopic(Topic):
    parent_page_types = ['Topic']
    subpage_types = []


class Topics(Page):
    subpage_types = ['Topic']
    template = 'topics.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['topics'] = self.get_topics()
        return context

    def get_topics(self, limit=12):
        return Topic.objects.live().public().order_by('title')[:limit]
