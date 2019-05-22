from wagtail.core.models import Page


class Topic(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'topic.html'
