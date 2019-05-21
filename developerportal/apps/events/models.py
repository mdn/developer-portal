from wagtail.core.models import Page


class Event(Page):
    subpage_types = []
    template = 'event.html'
