import datetime
from itertools import chain
from operator import attrgetter

from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey, TextField

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
from wagtail.core.fields import RichTextField, StreamBlock, StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from ..common.blocks import PersonalWebsiteBlock
from ..common.constants import RICH_TEXT_FEATURES_SIMPLE, ROLE_CHOICES
from ..common.models import BasePage
from .edit_handlers import CustomLabelFieldPanel


class PeopleTag(TaggedItemBase):
    content_object = ParentalKey(
        "People", on_delete=CASCADE, related_name="tagged_items"
    )


class People(BasePage):
    parent_page_types = ["home.HomePage", "content.ContentPage"]
    subpage_types = ["Person"]
    template = "people.html"

    # Content fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text="Optional short text description, max. 400 characters",
        max_length=400,
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=PeopleTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [FieldPanel("description")]

    # Meta panels
    meta_panels = [
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
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
        verbose_name_plural = "People"

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    def get_context(self, request):
        context = super().get_context(request)
        context["filters"] = self.get_filters()
        return context

    @property
    def people(self):
        return Person.published_objects.all().order_by("title")

    def get_filters(self):
        from ..topics.models import Topic

        return {
            "countries": True,
            "roles": True,
            "topics": Topic.published_objects.order_by("title"),
        }


class PersonTag(TaggedItemBase):
    content_object = ParentalKey(
        "Person", on_delete=CASCADE, related_name="tagged_items"
    )


class PersonTopic(Orderable):
    person = ParentalKey("Person", related_name="topics")
    topic = ForeignKey("topics.Topic", on_delete=CASCADE, related_name="+")

    panels = [PageChooserPanel("topic")]


class Person(BasePage):
    resource_type = "person"
    parent_page_types = ["People"]
    subpage_types = []
    template = "person.html"

    # Content fields
    job_title = CharField(max_length=250)
    role = CharField(max_length=250, choices=ROLE_CHOICES, default="staff")
    description = RichTextField(
        "About",
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text="Optional ‘About me’ section content, supports rich text",
    )
    image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
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

    # Meta
    city = CharField(max_length=250, blank=True, default="")
    country = CountryField()
    twitter = CharField(max_length=250, blank=True, default="")
    facebook = CharField(max_length=250, blank=True, default="")
    linkedin = CharField(max_length=250, blank=True, default="")
    github = CharField(max_length=250, blank=True, default="")
    email = CharField(max_length=250, blank=True, default="")
    websites = StreamField(
        StreamBlock([("website", PersonalWebsiteBlock())], max_num=3, required=False),
        null=True,
        blank=True,
        help_text="Optional links to any other personal websites",
    )
    keywords = ClusterTaggableManager(through=PersonTag, blank=True)

    # Content panels
    content_panels = [
        MultiFieldPanel(
            [
                CustomLabelFieldPanel("title", label="Full name"),
                FieldPanel("job_title"),
                FieldPanel("role"),
            ],
            heading="Details",
        ),
        FieldPanel("description"),
        MultiFieldPanel(
            [ImageChooserPanel("image")],
            heading="Image",
            help_text=(
                "Optional header image. If not specified a fallback will be used. "
                "This image is also shown when sharing this page via social media"
            ),
        ),
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
            [FieldPanel("city"), FieldPanel("country")],
            heading="Location",
            help_text=(
                "Location fields. The country field is also filterable "
                "via the people directory page."
            ),
        ),
        MultiFieldPanel([InlinePanel("topics")], heading="Topics interested in"),
        MultiFieldPanel(
            [
                FieldPanel("twitter"),
                FieldPanel("facebook"),
                FieldPanel("linkedin"),
                FieldPanel("github"),
                FieldPanel("email"),
            ],
            heading="Profiles",
            help_text="",
        ),
        StreamFieldPanel("websites"),
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
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

    # Tabs
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    @property
    def events(self):
        """
        Return upcoming events where this person is a speaker,
        ordered by start date
        """
        from ..events.models import Event

        upcoming_events = Event.published_objects.filter(
            start_date__gte=datetime.datetime.now()
        )

        speaker_events = Event.published_objects.none()

        for event in upcoming_events.all():
            # add the event to the list if the current person is a speaker
            if event.has_speaker(self):
                speaker_events = speaker_events | Event.published_objects.page(event)

        return speaker_events.order_by("start_date")

    @property
    def articles(self):
        """
        Return articles and external articles where this person is (one of) the authors,
        ordered by article date, most recent first
        """
        from ..articles.models import Article
        from ..externalcontent.models import ExternalArticle

        articles = Article.published_objects.none()
        external_articles = ExternalArticle.published_objects.none()

        all_articles = Article.published_objects.all()
        all_external_articles = ExternalArticle.published_objects.all()

        for article in all_articles:
            if article.has_author(self):
                articles = articles | Article.published_objects.page(article)

        for external_article in all_external_articles:
            if external_article.has_author(self):
                external_articles = external_articles | (
                    ExternalArticle.published_objects.page(external_article)
                )

        return sorted(
            chain(articles, external_articles), key=attrgetter("date"), reverse=True
        )

    @property
    def videos(self):
        """
        Return the most recent videos and external videos where this person is (one of)
        the speakers.
        """
        from ..videos.models import Video
        from ..externalcontent.models import ExternalVideo

        videos = Video.published_objects.none()
        external_videos = ExternalVideo.published_objects.none()

        all_videos = Video.published_objects.all()
        all_external_videos = ExternalVideo.published_objects.all()

        for video in all_videos:
            if video.has_speaker(self):
                videos = videos | Video.published_objects.page(video)

        for external_video in all_external_videos:
            if external_video.has_speaker(self):
                external_videos = external_videos | (
                    ExternalVideo.published_objects.page(external_video)
                )

        return sorted(
            chain(videos, external_videos), key=attrgetter("date"), reverse=True
        )

    @property
    def role_group(self):
        return {"slug": self.role, "title": dict(ROLE_CHOICES).get(self.role, "")}

    @property
    def country_group(self):
        return (
            {"slug": self.country.code.lower(), "title": self.country.name}
            if self.country
            else {"slug": ""}
        )
