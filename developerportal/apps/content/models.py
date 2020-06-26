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
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from ..common.constants import DESCRIPTION_MAX_LENGTH, RICH_TEXT_FEATURES_SIMPLE
from ..common.fields import CustomStreamField
from ..common.models import BasePage
from ..common.validators import check_for_svg_file


class ContentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ContentPage", on_delete=CASCADE, related_name="tagged_items"
    )


class ContentPage(BasePage):
    parent_page_types = ["home.HomePage", "content.ContentPage", "topics.Topic"]
    subpage_types = ["people.People", "content.ContentPage"]
    template = "content.html"

    # Content fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text=(
            "Optional short text description, "
            f"max. {DESCRIPTION_MAX_LENGTH} characters"
        ),
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    body = CustomStreamField(
        help_text=(
            "Main page body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        )
    )

    sidebar = CustomStreamField(
        null=True,
        blank=True,
        help_text=(
            "Sidebar page body content (narrower than main body). Rendered to the "
            "right of the main body content in desktop and below it in mobile."
            "Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )

    # Card fields
    card_title = CharField("Title", max_length=140, blank=True, default="")
    card_description = TextField("Description", max_length=140, blank=True, default="")
    card_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image in 16:9 aspect ratio",
    )
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
    nav_description = TextField(
        "Navigation description",
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        default="",
    )
    icon = FileField(
        upload_to="contentpage/icons",
        blank=True,
        default="",
        help_text=(
            "MUST be a black-on-transparent SVG icon ONLY, "
            "with no bitmap embedded in it."
        ),
        validators=[check_for_svg_file],
    )
    keywords = ClusterTaggableManager(through=ContentPageTag, blank=True)

    # Editor panel configuration
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        StreamFieldPanel("body"),
        StreamFieldPanel("sidebar"),
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
        FieldPanel(
            "nav_description",
            help_text="Text to display in the navigation with the title for this page.",
        ),
        MultiFieldPanel(
            [FieldPanel("icon")],
            heading="Theme",
            help_text=(
                "This icon will be used if, for example, this page is shown in a Menu"
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
                "Optional fields to override the default title and "
                "description for SEO purposes"
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

    # Search config
    search_fields = BasePage.search_fields + [  # Inherit search_fields from Page
        # "title" is already specced in BasePage
        index.SearchField("description"),
        index.SearchField("body"),
        # Add FilterFields for things we may be filtering on (eg topics)
        index.FilterField("slug"),
    ]
