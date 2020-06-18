from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    ForeignKey,
    TextField,
    URLField,
)

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import StreamBlock, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

from ..common.blocks import FeaturedExternalBlock
from ..common.constants import DESCRIPTION_MAX_LENGTH
from ..common.models import BasePage


class HomePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "HomePage", on_delete=CASCADE, related_name="tagged_items"
    )


class HomePage(BasePage):
    subpage_types = [
        "articles.Articles",
        "content.ContentPage",
        "events.Events",
        "people.People",
        "topics.Topics",
        "videos.Videos",
    ]
    template = "home.html"

    # Content fields
    subtitle = TextField(max_length=250, blank=True, default="")
    button_text = CharField(max_length=30, blank=True, default="")
    button_url = CharField(max_length=2048, blank=True, default="")
    image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
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
                (
                    "video",
                    PageChooserBlock(
                        target_model=(
                            "videos.Video",
                            # NB: ExternalVideo is NOT allowed on the homepage
                            # "externalcontent.ExternalVideo"
                        )
                    ),
                ),
            ],
            min_num=2,
            max_num=5,
            required=False,
        ),
        null=True,
        blank=True,
        help_text=(
            "Optional space for featured posts, videos or links, min. 2, max. 5. "
            "Note that External Video is NOT allowed here."
        ),
    )

    featured_people = StreamField(
        StreamBlock(
            [("person", PageChooserBlock(target_model="people.Person"))],
            max_num=3,
            required=False,
        ),
        null=True,
        blank=True,
        help_text="Optional featured people, max. 3",
    )

    about_title = TextField(max_length=250, blank=True, default="")
    about_subtitle = TextField(max_length=250, blank=True, default="")
    about_button_text = CharField(max_length=30, blank=True, default="")
    about_button_url = URLField(max_length=140, blank=True, default="")

    # Card fields
    card_title = CharField("Title", max_length=140, blank=True, default="")
    card_description = TextField(
        "Description", max_length=DESCRIPTION_MAX_LENGTH, blank=True, default=""
    )
    card_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
    )

    # Meta fields
    keywords = ClusterTaggableManager(through=HomePageTag, blank=True)

    # Editor panel configuration
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("subtitle"),
                FieldPanel("button_text"),
                FieldPanel("button_url"),
            ],
            heading="Header section",
            help_text="Optional fields for the header section",
        ),
        MultiFieldPanel(
            [ImageChooserPanel("image")],
            heading="Image",
            help_text=(
                "Optional image shown when sharing this page through social media"
            ),
        ),
        StreamFieldPanel("featured"),
        StreamFieldPanel("featured_people"),
        MultiFieldPanel(
            [
                FieldPanel("about_title"),
                FieldPanel("about_subtitle"),
                FieldPanel("about_button_text"),
                FieldPanel("about_button_url"),
            ],
            heading="About section",
            help_text="Optional section to explain more about Mozilla",
        ),
    ]

    # Card panels
    card_panels = [
        MultiFieldPanel(
            [
                FieldPanel("card_title"),
                FieldPanel("card_description"),
                ImageChooserPanel("card_image"),
            ],
            heading="Card overrides",
            help_text=(
                (
                    "Optional fields to override the default title, "
                    "description and image when this page is shown as a card"
                )
            ),
        )
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
                "Optional fields to override the default "
                "title and description for SEO purposes"
            ),
        )
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

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    @property
    def primary_topics(self):
        """The site’s top-level topics, i.e. topics without a parent topic."""
        from ..topics.models import Topic

        return Topic.published_objects.filter(parent_topics__isnull=True).order_by(
            "title"
        )
