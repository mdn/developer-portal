# pylint: disable=no-member
import datetime
import logging

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    FloatField,
    ForeignKey,
    Q,
    TextField,
    URLField,
)

from dateutil import relativedelta
from django_countries.fields import CountryField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
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

from ..common.blocks import AgendaItemBlock, ExternalSpeakerBlock, FeaturedExternalBlock
from ..common.constants import (
    DATE_PARAMS_QUERYSTRING_KEY,
    DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS,
    FUTURE_EVENTS_QUERYSTRING_VALUE,
    LOCATION_QUERYSTRING_KEY,
    PAGINATION_QUERYSTRING_KEY,
    PAST_EVENTS_QUERYSTRING_VALUE,
    RICH_TEXT_FEATURES_SIMPLE,
    TOPIC_QUERYSTRING_KEY,
)
from ..common.fields import CustomStreamField
from ..common.models import BasePage
from ..common.utils import (
    get_combined_events,
    get_past_event_cutoff,
    paginate_resources,
)
from ..topics.models import Topic

logger = logging.getLogger(__name__)


class EventsTag(TaggedItemBase):
    content_object = ParentalKey(
        "Events", on_delete=CASCADE, related_name="tagged_items"
    )


class EventTag(TaggedItemBase):
    content_object = ParentalKey(
        "Event", on_delete=CASCADE, related_name="tagged_items"
    )


class EventTopic(Orderable):
    event = ParentalKey("Event", related_name="topics")
    topic = ForeignKey("topics.Topic", on_delete=CASCADE, related_name="+")
    panels = [PageChooserPanel("topic")]


class EventSpeaker(Orderable):
    event = ParentalKey("Event", related_name="speaker")
    speaker = ForeignKey("people.Person", on_delete=CASCADE, related_name="+")
    panels = [PageChooserPanel("speaker")]


class Events(BasePage):

    EVENTS_PER_PAGE = 8

    parent_page_types = ["home.HomePage"]
    subpage_types = ["events.Event"]
    template = "events.html"

    # Content fields
    top_content = CustomStreamField(
        null=True,
        blank=True,
        help_text=(
            "Free-form content that appears above the 'Featured' section. "
            "Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )
    featured = StreamField(
        StreamBlock(
            [
                (
                    "event",
                    PageChooserBlock(
                        target_model=("events.Event", "externalcontent.ExternalEvent")
                    ),
                ),
                ("external_page", FeaturedExternalBlock()),
            ],
            max_num=2,
            required=False,
        ),
        null=True,
        blank=True,
        help_text=(
            "Optional space to show featured events. Note that these are "
            "rendered two-up, so please set 0 or 2"
        ),
    )
    body = CustomStreamField(
        null=True,
        blank=True,
        help_text=(
            "Main page body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )
    bottom_content = CustomStreamField(
        null=True,
        blank=True,
        help_text=(
            "Free-form content that appears below the list of Events. "
            "Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=EventsTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("top_content"),
        StreamFieldPanel("featured"),
        StreamFieldPanel("body"),
        StreamFieldPanel("bottom_content"),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                ImageChooserPanel("social_image"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default title and description "
                "for SEO purposes"
            ),
        )
    ]

    # Settings panels
    settings_panels = BasePage.settings_panels + [
        FieldPanel("slug"),
        FieldPanel("show_in_menus"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    class Meta:
        verbose_name_plural = "Events"

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    def get_context(self, request):
        context = super().get_context(request)
        context["filters"] = self.get_filters(request)
        context["events"] = self.get_events(request)
        return context

    def _build_date_q(self, date_params):
        """Suport filtering events by 'all future events' or 'all past events' Booleans.

        Arguments:
            date_params: List(str) -- list of sentinel strings of
                FUTURE_EVENTS_QUERYSTRING_VALUE and/or
                PAST_EVENTS_QUERYSTRING_VALUE.

                Specifying FUTURE_EVENTS_QUERYSTRING_VALUE will return all FUTURE events
                Specifying PAST_EVENTS_QUERYSTRING_VALUE will return all PAST events
                Specifying both will return ALL events, past and future
                Specifying neither will trigger the default behaviour: to return events
                    between now and DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS months time

        Returns:
            django.models.QuerySet -- configured QuerySet based on arguments.
        """

        # Assemble facts from the year_months querystring data
        past_events_flag = PAST_EVENTS_QUERYSTRING_VALUE in date_params
        future_events_flag = FUTURE_EVENTS_QUERYSTRING_VALUE in date_params

        if past_events_flag and not future_events_flag:
            date_q = Q(start_date__lte=get_past_event_cutoff())
        elif not past_events_flag and future_events_flag:
            date_q = Q(start_date__gte=get_past_event_cutoff())
        elif past_events_flag and future_events_flag:
            date_q = Q()  # Because we don't need to restrict
        else:
            window_start = get_past_event_cutoff()
            window_end = window_start + relativedelta.relativedelta(
                months=DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS,
                days=1,  # Because get_past_event_cutoff() goes back to yesterday
            )
            date_q = Q(start_date__gte=window_start, start_date__lte=window_end)
        return date_q

    def get_events(self, request):
        """Return filtered future events in chronological order"""

        countries = request.GET.getlist(LOCATION_QUERYSTRING_KEY)
        date_params = request.GET.getlist(DATE_PARAMS_QUERYSTRING_KEY)
        topics = request.GET.getlist(TOPIC_QUERYSTRING_KEY)

        countries_q = Q(country__in=countries) if countries else Q()
        topics_q = Q(topics__topic__slug__in=topics) if topics else Q()

        # date_params need a little more logic to construct
        date_q = self._build_date_q(date_params)

        combined_q = Q()
        if countries_q:
            combined_q.add(countries_q, Q.AND)
        if date_q:
            combined_q.add(date_q, Q.AND)
        if topics_q:
            combined_q.add(topics_q, Q.AND)

        events = get_combined_events(self, reverse=False, q_object=combined_q)

        events = paginate_resources(
            events,
            page_ref=request.GET.get(PAGINATION_QUERYSTRING_KEY),
            per_page=self.EVENTS_PER_PAGE,
        )

        return events

    def get_relevant_countries(self):
        # Relevant here means a country that a published Event is or was in
        raw_countries = (
            event.country
            for event in Event.published_objects.distinct("country").order_by("country")
            if event.country
        )

        # Need to do a separate sort by country name because "Online" has a fake country
        # code of QQ - see settings.base.COUNTRIES_OVERRIDE
        sorted_raw_countries = sorted(raw_countries, key=lambda country: country.name)

        return [
            {"code": country.code, "name": country.name}
            for country in sorted_raw_countries
        ]

    def get_event_date_options(self, request):
        return {
            "options_selected": (
                (
                    PAST_EVENTS_QUERYSTRING_VALUE
                    in request.GET.getlist(DATE_PARAMS_QUERYSTRING_KEY, [])
                )
                or (
                    FUTURE_EVENTS_QUERYSTRING_VALUE
                    in request.GET.getlist(DATE_PARAMS_QUERYSTRING_KEY, [])
                )
            ),
            "options": [
                {"value": PAST_EVENTS_QUERYSTRING_VALUE, "label": "Past events"},
                {"value": FUTURE_EVENTS_QUERYSTRING_VALUE, "label": "Future events"},
            ],
        }

    def get_filters(self, request):
        return {
            "countries": self.get_relevant_countries(),
            "event_dates": self.get_event_date_options(request),
            "topics": Topic.published_objects.order_by("title"),
        }


class Event(BasePage):
    resource_type = "event"
    parent_page_types = ["events.Events"]
    subpage_types = []
    template = "event.html"

    # Content fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text="Optional short text description, max. 400 characters",
        max_length=400,
    )
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    latitude = FloatField(blank=True, null=True)  # DEPRECATED
    longitude = FloatField(blank=True, null=True)  # DEPRECATED
    register_url = URLField("Register URL", blank=True, null=True)
    official_website = URLField("Official website", blank=True, default="")
    event_content = URLField(
        "Event content",
        blank=True,
        default="",
        help_text=(
            "Link to a page (in this site or elsewhere) "
            "with content about this event."
        ),
    )

    body = CustomStreamField(
        blank=True,
        null=True,
        help_text=(
            "Optional body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )
    venue_name = CharField(max_length=100, blank=True, default="")  # DEPRECATED
    venue_url = URLField(
        "Venue URL", max_length=100, blank=True, default=""
    )  # DEPRECATED
    address_line_1 = CharField(max_length=100, blank=True, default="")  # DEPRECATED
    address_line_2 = CharField(max_length=100, blank=True, default="")  # DEPRECATED
    address_line_3 = CharField(max_length=100, blank=True, default="")  # DEPRECATED
    city = CharField(max_length=100, blank=True, default="")
    state = CharField(
        "State/Province/Region", max_length=100, blank=True, default=""
    )  # DEPRECATED
    zip_code = CharField(
        "Zip/Postal code", max_length=100, blank=True, default=""
    )  # DEPRECATED
    country = CountryField(blank=True, default="")
    agenda = StreamField(
        StreamBlock([("agenda_item", AgendaItemBlock())], required=False),
        blank=True,
        null=True,
        help_text="Optional list of agenda items for this event",
    )  # DEPRECATED
    speakers = StreamField(
        StreamBlock(
            [
                ("speaker", PageChooserBlock(target_model="people.Person")),
                ("external_speaker", ExternalSpeakerBlock()),
            ],
            required=False,
        ),
        blank=True,
        null=True,
        help_text="Optional list of speakers for this event",
    )  # DEPRECATED

    # Card fields
    card_title = CharField("Title", max_length=140, blank=True, default="")
    card_description = TextField("Description", max_length=400, blank=True, default="")
    card_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image in 16:9 aspect ratio",
    )
    card_image_3_2 = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image in 3:2 aspect ratio",
    )
    # Meta fields
    keywords = ClusterTaggableManager(through=EventTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("register_url"),
                FieldPanel("official_website"),
                FieldPanel("event_content"),
            ],
            heading="Event details",
            classname="collapsible",
            help_text=(
                "'Event content' should be used to link to a page (anywhere) "
                "which summarises the content of the event"
            ),
        ),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [FieldPanel("city"), FieldPanel("country")],
            heading="Event location",
            classname="collapsible",
            help_text=("The city and country are also shown on event cards"),
        ),
    ]

    # Card panels
    card_panels = [
        FieldPanel("card_title"),
        FieldPanel("card_description"),
        MultiFieldPanel(
            [ImageChooserPanel("card_image")],
            heading="16:9 Image",
            help_text=(
                "Image used for representing this page as a Card. "
                "Should be 16:9 aspect ratio. "
                "If not specified a fallback will be used. "
                "This image is also shown when sharing this page via social "
                "media unless a social image is specified."
            ),
        ),
        MultiFieldPanel(
            [ImageChooserPanel("card_image_3_2")],
            heading="3:2 Image",
            help_text=(
                "Image used for representing this page as a Card. "
                "Should be 3:2 aspect ratio. "
                "If not specified a fallback will be used. "
            ),
        ),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel(
            [InlinePanel("topics")],
            heading="Topics",
            help_text=(
                "These are the topic pages the event will appear on. The first topic "
                "in the list will be treated as the primary topic and will be shown "
                "in the page’s related content."
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                ImageChooserPanel("social_image"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default title and description "
                "for SEO purposes"
            ),
        ),
    ]

    # Settings panels
    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def is_upcoming(self):
        """Returns whether an event is in the future."""
        return self.start_date >= get_past_event_cutoff()

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the event."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None

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
        if self.end_date and self.end_date != self.start_date:
            event_dates += " – "  # rather than &ndash; so we don't have to mark safe
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

    def has_speaker(self, person):
        for speaker in self.speakers:  # pylint: disable=not-an-iterable
            if speaker.block_type == "speaker" and str(speaker.value) == str(
                person.title
            ):
                return True
        return False

    @property
    def summary_meta(self):
        """Return a simple plaintext string that can be used
        as a standfirst"""

        summary = ""
        if self.event_dates:
            summary += self.event_dates
            if self.city or self.country:
                summary += " | "

        if self.city:
            summary += self.city
            if self.country:
                summary += ", "
        if self.country:
            summary += self.country.name
        return summary
