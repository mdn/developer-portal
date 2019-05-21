from wagtail.core.models import Page


class Mozillian(Page):
    subpage_types = []
    template = 'mozillian.html'
