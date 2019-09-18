from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey, TextField

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
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from ..common.fields import CustomStreamField


class ContentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ContentPage", on_delete=CASCADE, related_name="tagged_items"
    )


class ContentPage(Page):
    parent_page_types = ["home.HomePage", "content.ContentPage"]
    subpage_types = ["people.People", "content.ContentPage"]
    template = "content.html"

    # Content fields
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
    keywords = ClusterTaggableManager(through=ContentPageTag, blank=True)

    # Editor panel configuration
    content_panels = Page.content_panels + [
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
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default title and "
                "description for SEO purposes"
            ),
        )
    ]

    # Settings panels
    settings_panels = [FieldPanel("slug"), FieldPanel("show_in_menus")]

    # Tabs
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )
