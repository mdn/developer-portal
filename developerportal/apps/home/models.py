from wagtail.core.models import Page


class HomePage(Page):
    subpage_types = [
        'articles.Articles',
        'topics.Topic',
    ]
    template = 'home.html'
