# pylint: disable=no-member

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    FileField,
    ForeignKey,
    TextField,
)

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

from ..common.blocks import FeaturedExternalBlock
from ..common.constants import RICH_TEXT_FEATURES_SIMPLE
from ..common.models import BasePage
from ..common.utils import (
    get_combined_articles,
    get_combined_events,
    get_combined_videos,
    get_past_event_cutoff,
)
from ..common.validators import check_for_svg_file


class TopicsTag(TaggedItemBase):
    content_object = ParentalKey(
        "Topics", on_delete=CASCADE, related_name="tagged_items"
    )


class TopicTag(TaggedItemBase):
    content_object = ParentalKey(
        "Topic", on_delete=CASCADE, related_name="tagged_items"
    )


class TopicPerson(Orderable):
    topic = ParentalKey("Topic", related_name="people")
    person = ForeignKey("people.Person", on_delete=CASCADE, related_name="+")

    panels = [PageChooserPanel("person")]


class ParentTopic(Orderable):
    child = ParentalKey("Topic", related_name="parent_topics")
    parent = ParentalKey("Topic", on_delete=CASCADE, related_name="child_topics")

    panels = [PageChooserPanel("child"), PageChooserPanel("parent")]


class Topic(BasePage):
    resource_type = "topic"
    parent_page_types = ["Topics"]
    subpage_types = ["Topic", "content.ContentPage"]
    template = "topic.html"

    # Content fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text="Optional short text description, max. 400 characters",
        max_length=400,
    )
    featured = StreamField(
        StreamBlock(
            [
                (
                    "post",
                    PageChooserBlock(
                        target_model=(
                            "articles.Article",
                            "externalcontent.ExternalArticle",
                        )
                    ),
                ),
                ("external_page", FeaturedExternalBlock()),
            ],
            min_num=2,
            max_num=5,
            required=True,
        ),
        null=True,
        blank=True,
        help_text="Optional space for featured items, max. 5",
    )
    #  "What We've Been Working On" panel
    recent_work = StreamField(
        StreamBlock(
            [
                (
                    "post",
                    PageChooserBlock(
                        target_model=(
                            "articles.Article",
                            "externalcontent.ExternalArticle",
                        )
                    ),
                ),
                ("external_page", FeaturedExternalBlock()),
                (
                    "video",
                    PageChooserBlock(
                        target_model=("videos.Video", "externalcontent.ExternalVideo")
                    ),
                ),
            ],
            max_num=4,
            required=False,
        ),
        null=True,
        blank=True,
        help_text=(
            "Optional space for featured posts, videos or links, min. 1, max. 4."
        ),
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
        help_text="An image in 16:9 aspect ratio",
    )

    # Meta
    nav_description = TextField(
        "Navigation description", max_length=400, blank=True, default=""
    )
    icon = FileField(
        upload_to="topics/icons",
        blank=True,
        default="",
        help_text=(
            "MUST be a black-on-transparent SVG icon ONLY, "
            "with no bitmap embedded in it."
        ),
        validators=[check_for_svg_file],
    )
    keywords = ClusterTaggableManager(through=TopicTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        StreamFieldPanel("featured"),
        StreamFieldPanel("recent_work"),
        MultiFieldPanel(
            [InlinePanel("people")],
            heading="Content by",
            help_text="Optional list of people who create content on this topic",
        ),
    ]

    # Card panels
    card_panels = [
        FieldPanel(
            "card_title",
            help_text=(
                "Title displayed when this page is "
                "represented by a card in a list of items. "
                "If blank, the page's title is used."
            ),
        ),
        FieldPanel(
            "card_description",
            help_text=(
                "Summary text displayed when this page is "
                "represented by a card in a list of items. "
                "If blank, the page's description is used."
            ),
        ),
        MultiFieldPanel(
            [ImageChooserPanel("card_image")],
            heading="16:9 Image",
            help_text=(
                "Image used for representing this page as a Card. "
                "Must be 16:9 aspect ratio. "
                "If not specified a fallback will be used. "
                "This image is also used for social media posts, unless overriden"
            ),
        ),
    ]

    # Meta panels
    meta_panels = [
        FieldPanel(
            "nav_description",
            help_text="Text to display in the navigation with the title for this page.",
        ),
        MultiFieldPanel(
            [
                InlinePanel("parent_topics", label="Parent topic(s)"),
                InlinePanel("child_topics", label="Child topic(s)"),
            ],
            heading="Parent/child topic(s)",
            classname="collapsible collapsed",
            help_text=(
                "Topics with no parent (i.e. top-level topics) will be "
                "listed on the home page. Child topics are listed "
                "on the parent topic’s page."
            ),
        ),
        MultiFieldPanel([FieldPanel("icon")], heading="Theme"),
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                ImageChooserPanel("social_image"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default "
                "title and description for SEO purposes"
            ),
        ),
    ]

    # Settings panels
    settings_panels = BasePage.settings_panels + [
        FieldPanel("slug"),
        FieldPanel("show_in_menus"),
    ]

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
    def articles(self):
        return get_combined_articles(self, topics__topic__pk=self.pk)

    @property
    def events(self):
        """Return upcoming events for this topic,
        ignoring events in the past, ordered by start date"""
        return get_combined_events(
            self, topics__topic__pk=self.pk, start_date__gte=get_past_event_cutoff()
        )

    @property
    def experts(self):
        """Return Person instances for topic experts"""
        return [person.person for person in self.people.all()]

    @property
    def videos(self):
        """Return the latest videos and external videos for this topic. """
        return get_combined_videos(self, topics__topic__pk=self.pk)

    @property
    def subtopics(self):
        return [topic.child for topic in self.child_topics.all()]


class Topics(BasePage):
    resource_type = "topics"  # NB note plural
    parent_page_types = ["home.HomePage"]
    subpage_types = ["Topic"]
    template = "topics.html"

    # Cache keys associated with this Page type - also see common.models.BasePage
    CACHE_KEY_TOPICS_TITLE = "topics-titles"
    _bulk_invalidation_cache_keys = [CACHE_KEY_TOPICS_TITLE]

    # Meta fields
    keywords = ClusterTaggableManager(through=TopicsTag, blank=True)

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
                "Optional fields to override the default "
                "title and description for SEO purposes"
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
            ObjectList(BasePage.content_panels, heading="Content"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    class Meta:
        verbose_name_plural = "Topics"

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    @property
    def topics(self):
        return Topic.published_objects.order_by("title")
