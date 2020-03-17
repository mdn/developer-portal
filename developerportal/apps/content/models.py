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

from ..common.constants import RICH_TEXT_FEATURES_SIMPLE
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
        help_text="Optional short text description, max. 400 characters",
        max_length=400,
    )
    hero_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
    )
    body = CustomStreamField(
        help_text=(
            "Main page body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        )
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
    )

    # Meta fields
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
        MultiFieldPanel(
            [ImageChooserPanel("hero_image")],
            heading="Hero image",
            help_text="Image should be at least 1024px x 438px (21:9 aspect ratio)",
        ),
        StreamFieldPanel("body"),
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
