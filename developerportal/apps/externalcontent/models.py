# pylint: disable=no-member
import datetime
import logging

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    ForeignKey,
    URLField,
)
from django.http import HttpResponseRedirect

from django_countries.fields import CountryField
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import RichTextField, StreamBlock, StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from ..common.blocks import ExternalAuthorBlock
from ..common.constants import RICH_TEXT_FEATURES_SIMPLE
from ..common.models import BasePage

logger = logging.getLogger(__name__)


class ExternalContent(BasePage):
    is_external = True
    subpage_types = []

    # Card fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text="Optional short text description, max. 400 characters",
        max_length=400,
    )
    external_url = URLField(
        "URL",
        blank=True,
        default="",
        help_text=(
            "The URL that this content links to, max. 2048 characters "
            "for compatibility with older web browsers"
        ),
        max_length=2048,
    )
    image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
    )

    card_panels = BasePage.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel(
            [ImageChooserPanel("image")],
            heading="Image",
            help_text=(
                "Optional header image. If not specified a fallback will be used. "
                "This image is also shown when sharing this page via social media"
            ),
        ),
        FieldPanel("external_url"),
    ]

    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(card_panels, heading="Card"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    class Meta:
        verbose_name_plural = "External Content"

    def get_full_url(self, request=None):
        return self.external_url

    def get_url(self, request=None, current_site=None):
        return self.external_url

    def relative_url(self, current_site, request=None):
        return self.external_url

    @property
    def url(self):
        return self.external_url

    def serve_preview(self, request, mode_name):
        # ExternalContent subclasses don't preview like regular Pages: we just need
        # to show where they link to.
        return HttpResponseRedirect(self.external_url)


class ExternalArticleTopic(Orderable):
    article = ParentalKey("ExternalArticle", on_delete=CASCADE, related_name="topics")
    topic = ForeignKey(
        "topics.Topic", on_delete=CASCADE, related_name="external_articles"
    )

    panels = [PageChooserPanel("topic")]


class ExternalArticle(ExternalContent):
    class Meta:
        verbose_name = "External Post"
        verbose_name_plural = "External Posts"

    resource_type = "article"  #  if you change this, amend the related CSS, too

    date = DateField(
        "External Post date",
        default=datetime.date.today,
        help_text="The date the external post was published",
    )
    authors = StreamField(
        StreamBlock(
            [
                ("author", PageChooserBlock(target_model="people.Person")),
                ("external_author", ExternalAuthorBlock()),
            ],
            required=False,
        ),
        blank=True,
        null=True,
        help_text=(
            "Optional list of the external post's authors. "
            "Use ‘External author’ to add "
            "guest authors without creating a profile on the system"
        ),
    )
    read_time = CharField(
        max_length=30,
        blank=True,
        help_text=(
            "Optional, approximate read-time for this external post, "
            "e.g. “2 mins”. This is shown as a small hint when the "
            "external post is displayed as a card."
        ),
    )

    meta_panels = [
        FieldPanel("date"),
        StreamFieldPanel("authors"),
        MultiFieldPanel(
            [InlinePanel("topics")],
            heading="Topics",
            help_text="The topic pages this external post will appear on",
        ),
        FieldPanel("read_time"),
    ]

    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(ExternalContent.card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def article(self):
        return self

    @property
    def month_group(self):
        return self.date.replace(day=1)

    def has_author(self, person):
        for author in self.authors:  # pylint: disable=not-an-iterable
            if author.block_type == "author" and str(author.value) == str(person.title):
                return True
        return False


class ExternalEventTopic(Orderable):
    event = ParentalKey("ExternalEvent", on_delete=CASCADE, related_name="topics")
    topic = ForeignKey(
        "topics.Topic", on_delete=CASCADE, related_name="external_events"
    )

    panels = [PageChooserPanel("topic")]


class ExternalEventSpeaker(Orderable):
    article = ParentalKey("ExternalEvent", on_delete=CASCADE, related_name="speakers")
    speaker = ForeignKey(
        "people.Person", on_delete=CASCADE, related_name="external_events"
    )

    panels = [PageChooserPanel("speaker")]


class ExternalEvent(ExternalContent):
    resource_type = "event"

    start_date = DateField(
        default=datetime.date.today,
        help_text="The date the event is scheduled to start",
    )
    end_date = DateField(
        blank=True, null=True, help_text="The date the event is scheduled to end"
    )
    city = CharField(max_length=100, blank=True, default="")
    country = CountryField(blank=True, default="")

    meta_panels = [
        MultiFieldPanel(
            [FieldPanel("start_date"), FieldPanel("end_date")], heading="Event details"
        ),
        MultiFieldPanel(
            [FieldPanel("city"), FieldPanel("country")], heading="Event address"
        ),
        InlinePanel(
            "topics",
            heading="Topics",
            help_text=(
                "Optional topics this event is associated with. "
                "Adds the event to the list of events on those topic pages"
            ),
        ),
        InlinePanel(
            "speakers",
            heading="Speakers",
            help_text=(
                "Optional speakers associated with this event. "
                "Adds the event to the list of events on their profile pages"
            ),
        ),
    ]

    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(ExternalContent.card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def event(self):
        return self

    @property
    def month_group(self):
        return self.start_date.replace(day=1)

    @property
    def country_group(self):
        return (
            {"slug": self.country.code.lower(), "title": self.country.name}
            if self.country
            else {"slug": ""}
        )

    @property
    def event_dates(self):
        """Return a formatted string of the event start and end dates"""
        event_dates = self.start_date.strftime("%b %-d")
        if self.end_date:
            event_dates += " &ndash; "
            start_month = self.start_date.strftime("%m")
            if self.end_date.strftime("%m") == start_month:
                event_dates += self.end_date.strftime("%-d")
            else:
                event_dates += self.end_date.strftime("%b %-d")
        return event_dates

    @property
    def event_dates_full(self):
        """Return a formatted string of the event start and end dates,
        including the year"""
        return self.event_dates + self.start_date.strftime(", %Y")


class ExternalVideoTopic(Orderable):
    video = ParentalKey("ExternalVideo", on_delete=CASCADE, related_name="topics")
    topic = ForeignKey(
        "topics.Topic", on_delete=CASCADE, related_name="external_videos"
    )

    panels = [PageChooserPanel("topic")]


class ExternalVideoPerson(Orderable):
    article = ParentalKey("ExternalVideo", on_delete=CASCADE, related_name="people")
    person = ForeignKey(
        "people.Person", on_delete=CASCADE, related_name="external_videos"
    )

    panels = [PageChooserPanel("person")]


class ExternalVideo(ExternalContent):
    resource_type = "video"
    is_external = True

    # Meta fields
    date = DateField(
        "Video date",
        default=datetime.date.today,
        help_text="The date the video was published",
    )
    speakers = StreamField(
        StreamBlock(
            [("speaker", PageChooserBlock(target_model="people.Person"))],
            required=False,
        ),
        blank=True,
        null=True,
        help_text="Optional list of people associated with or starring in the video",
    )
    duration = CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text=(
            "Optional video duration in MM:SS format e.g. “12:34”. "
            "Shown when the video is displayed as a card"
        ),
    )

    meta_panels = [
        FieldPanel("date"),
        StreamFieldPanel("speakers"),
        InlinePanel("topics", heading="Topics"),
        FieldPanel("duration"),
    ]

    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(ExternalContent.card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def video(self):
        return self

    def has_speaker(self, person):
        for speaker in self.speakers:  # pylint: disable=not-an-iterable
            if str(speaker.value) == str(person.title):
                return True
        return False
