from wagtail.core.models import Page


class Article(Page):
    template = 'article.html'
