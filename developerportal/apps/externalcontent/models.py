from django.db.models import CharField, URLField

from wagtail.admin.edit_handlers import FieldPanel, ObjectList, TabbedInterface
from wagtail.core.models import Page

class ExternalContent(Page):
    subpage_types = []

    external_url = URLField(max_length=2048, blank=True, default='')

    content_panels = Page.content_panels + [
        FieldPanel('external_url'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    def get_full_url(self, request=None):
        return self.external_url

    def get_url(self, request=None, current_site=None):
        return self.external_url

    def relative_url(self, current_site, request=None):
        return self.external_url

    @property
    def url(self):
        return self.external_url


class ExternalArticle(ExternalContent):
    readtime = CharField(max_length=30, blank=True, default='0 min read')

    content_panels = Page.content_panels + [
        FieldPanel('external_url'),
        FieldPanel('readtime'),
    ]


class ExternalEvent(ExternalContent):
    pass


class ExternalVideo(ExternalContent):
    video_duration = CharField(max_length=30, blank=True, default='0:00')

    content_panels = Page.content_panels + [
        FieldPanel('external_url'),
        FieldPanel('video_duration'),
    ]
