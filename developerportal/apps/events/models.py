from wagtail.core.models import Page


class Event(Page):
    resource_type = 'event'
    subpage_types = []
    template = 'event.html'
