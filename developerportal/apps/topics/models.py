from wagtail.core.models import Page


class Topic(Page):
    sub_page_types = []
    template = 'topic.html'
