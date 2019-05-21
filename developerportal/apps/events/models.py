from wagtail.core.models import Page


class Event(Page):
    sub_page_types = []
    template = 'event.html'
