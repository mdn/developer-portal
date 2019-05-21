from wagtail.core.models import Page


class Topic(Page):
    subpage_types = []
    template = 'topic.html'
