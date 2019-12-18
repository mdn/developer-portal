# pylint: disable=no-member
import datetime

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
from django.utils.safestring import mark_safe
from django.utils.timezone import now as tz_now

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
    COUNTRY_QUERYSTRING_KEY,
    PAGINATION_QUERYSTRING_KEY,
    RICH_TEXT_FEATURES_SIMPLE,
    TOPIC_QUERYSTRING_KEY,
    YEAR_MONTH_QUERYSTRING_KEY,
)
from ..common.fields import CustomStreamField
from ..common.models import BasePage
from ..common.utils import get_combined_events, paginate_resources
from ..topics.models import Topic


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

    # Note that we only paginate PAST events right now, and not the future ones
    PAST_EVENTS_PER_PAGE = 20

    parent_page_types = ["home.HomePage"]
    subpage_types = ["events.Event"]
    template = "events.html"

    # Content fields
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
            max_num=1,
            required=False,
        ),
        null=True,
        blank=True,
        help_text="Optional space to show a featured event",
    )
    body = CustomStreamField(
        help_text=(
            "Main page body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        )
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=EventsTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("featured"),
        StreamFieldPanel("body"),
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
    settings_panels = [FieldPanel("slug"), FieldPanel("show_in_menus")]

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
        context["filters"] = self.get_filters()
        context["events"] = self.get_upcoming_events(request)
        past_events, total_past_events = self.get_past_events(request)
        context["past_events"] = past_events
        context["show_past_event_pagination"] = (
            total_past_events > self.PAST_EVENTS_PER_PAGE
        )
        return context

    def _year_months_to_years_and_months_tuples(self, year_months):
        """For the given list of "YYYY-MM" strings, return a list of tuples
        containg the year and and month, still as strings.

        Example input:  ["2020-03", "2020-12"]
        Example output: [("2020", "03"), ("2020", "12")]
        """

        if not year_months:
            return []
        return [tuple(x.split("-")) for x in [y for y in year_months if y]]

    def _build_date_q(self, year_months):
        "Support filtering future events by selected year-month pair(s)"
        default_future_events_q = Q(start_date__gte=tz_now().date())

        years_and_months_tuples = self._year_months_to_years_and_months_tuples(
            year_months
        )
        if not years_and_months_tuples:
            # Covers case where no year_months
            return default_future_events_q

        # Build a Q where it's (Month X AND Year X) OR (Month Y AND Year Y), etc
        overall_date_q = None

        for year, month in years_and_months_tuples:
            date_q = Q(**{"start_date__year": year})
            date_q.add(Q(**{"start_date__month": month}), Q.AND)

            if overall_date_q is None:
                overall_date_q = date_q
            else:
                overall_date_q.add(date_q, Q.OR)

        # Finally, ensure we don't include past events here (ie, same month as
        # selected but before today)
        overall_date_q.add(default_future_events_q, Q.AND)
        return overall_date_q

    def get_upcoming_events(self, request):
        """Return filtered future events in chronological order"""
        # These are not paginated but ARE filtered

        countries = request.GET.getlist(COUNTRY_QUERYSTRING_KEY)
        years_months = request.GET.getlist(YEAR_MONTH_QUERYSTRING_KEY)
        topics = request.GET.getlist(TOPIC_QUERYSTRING_KEY)

        countries_q = Q(country__in=countries) if countries else Q()
        topics_q = Q(topics__topic__slug__in=topics) if topics else Q()

        # year_months need splitting to make them work
        date_q = self._build_date_q(years_months)

        combined_q = Q()
        if countries_q:
            combined_q.add(countries_q, Q.AND)
        if date_q:
            combined_q.add(date_q, Q.AND)
        if topics_q:
            combined_q.add(topics_q, Q.AND)

        # Combined_q will always have something because it includes
        # the start_date__gte test
        events = get_combined_events(self, q_object=combined_q)

        return events

    def get_past_events(self, request):
        """Return paginated past events in reverse chronological order,
        plus a count of how many there are in total
        """
        past_events = get_combined_events(
            self, reverse=True, start_date__lt=tz_now().date()
        )
        total_past_events = len(past_events)

        past_events = paginate_resources(
            past_events,
            page_ref=request.GET.get(PAGINATION_QUERYSTRING_KEY),
            per_page=self.PAST_EVENTS_PER_PAGE,
        )
        return past_events, total_past_events

    def get_relevant_countries(self):
        # Relevant here means a country that a published Event is or was in
        raw_countries = (
            event.country
            for event in Event.published_objects.filter(start_date__gte=tz_now().date())
            .distinct("country")
            .order_by("country")
            if event.country
        )

        return [
            {"code": country.code, "name": country.name} for country in raw_countries
        ]

    def get_relevant_dates(self):
        # Relevant here means a date for a published *future* event
        # TODO: would be good to cache this for short period of time
        raw_events = get_combined_events(self, start_date__gte=tz_now().date())
        return sorted([event.start_date for event in raw_events])

    def get_filters(self):
        return {
            "countries": self.get_relevant_countries(),
            "dates": self.get_relevant_dates(),
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
    image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
    )
    start_date = DateField(default=datetime.date.today)
    end_date = DateField(blank=True, null=True)
    latitude = FloatField(blank=True, null=True)
    longitude = FloatField(blank=True, null=True)
    register_url = URLField("Register URL", blank=True, null=True)
    body = CustomStreamField(
        blank=True,
        null=True,
        help_text=(
            "Optional body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )
    venue_name = CharField(max_length=100, blank=True, default="")
    venue_url = URLField("Venue URL", max_length=100, blank=True, default="")
    address_line_1 = CharField(max_length=100, blank=True, default="")
    address_line_2 = CharField(max_length=100, blank=True, default="")
    address_line_3 = CharField(max_length=100, blank=True, default="")
    city = CharField(max_length=100, blank=True, default="")
    state = CharField("State/Province/Region", max_length=100, blank=True, default="")
    zip_code = CharField("Zip/Postal code", max_length=100, blank=True, default="")
    country = CountryField(blank=True, default="")
    agenda = StreamField(
        StreamBlock([("agenda_item", AgendaItemBlock())], required=False),
        blank=True,
        null=True,
        help_text="Optional list of agenda items for this event",
    )
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
    )

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
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=EventTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel(
            [ImageChooserPanel("image")],
            heading="Image",
            help_text=(
                "Optional header image. If not specified a fallback will be used. "
                "This image is also shown when sharing this page via social media"
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
                FieldPanel("register_url"),
            ],
            heading="Event details",
            classname="collapsible",
            help_text=mark_safe(
                "Optional time and location information for this event. Latitude and "
                "longitude are used to show a map of the event’s location. For more "
                "information on finding these values for a given location, "
                "'<a href='https://support.google.com/maps/answer/18539'>"
                "see this article</a>"
            ),
        ),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("venue_name"),
                FieldPanel("venue_url"),
                FieldPanel("address_line_1"),
                FieldPanel("address_line_2"),
                FieldPanel("address_line_3"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("zip_code"),
                FieldPanel("country"),
            ],
            heading="Event address",
            classname="collapsible",
            help_text=(
                "Optional address fields. The city and country are also shown "
                "on event cards"
            ),
        ),
        StreamFieldPanel("agenda"),
        StreamFieldPanel("speakers"),
    ]

    # Card panels
    card_panels = [
        FieldPanel("card_title"),
        FieldPanel("card_description"),
        ImageChooserPanel("card_image"),
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
    settings_panels = [FieldPanel("slug")]

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
        return self.start_date >= tz_now().date()

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

    def has_speaker(self, person):
        for speaker in self.speakers:  # pylint: disable=not-an-iterable
            if speaker.block_type == "speaker" and str(speaker.value) == str(
                person.title
            ):
                return True
        return False
