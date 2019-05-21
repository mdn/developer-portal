from wagtail.core.models import Page


class Mozillian(Page):
    sub_page_types = []
    template = 'mozillian.html'
