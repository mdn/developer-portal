from wagtail.core.models import Page


class HomePage(Page):
    subpage_types = []
    template = 'home.html'
