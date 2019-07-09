import datetime

from django.db.models import CharField, DateField, ForeignKey, SET_NULL, TextField, URLField

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class ExternalContent(Page):
    subpage_types = []

    external_url = URLField(max_length=2048, blank=True, default='')
    header_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('external_url'),
        ImageChooserPanel('header_image'),
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
    read_time = CharField(max_length=30, blank=True, default='0 min read')

    content_panels = ExternalContent.content_panels + [
        FieldPanel('read_time'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])


class ExternalEvent(ExternalContent):
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    venue = TextField(max_length=250, blank=True, default='')

    content_panels = ExternalContent.content_panels + [
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
            FieldPanel('venue'),
        ], heading='Event details'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])


class ExternalVideo(ExternalContent):
    video_duration = CharField(max_length=30, blank=True, default='0:00')

    content_panels = ExternalContent.content_panels + [
        FieldPanel('video_duration'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])
