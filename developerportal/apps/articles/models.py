# pylint: disable=no-member
import datetime

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    ForeignKey,
    Q,
    TextField,
)
from django.template.loader import render_to_string

import readtime
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
from wagtail.search import index

from ..common.blocks import ExternalAuthorBlock, ExternalLinkBlock
from ..common.constants import (
    DESCRIPTION_MAX_LENGTH,
    PAGINATION_QUERYSTRING_KEY,
    RICH_TEXT_FEATURES_SIMPLE,
    SEARCH_QUERYSTRING_KEY,
    TOPIC_QUERYSTRING_KEY,
)
from ..common.fields import CustomStreamField
from ..common.models import BasePage
from ..common.utils import get_combined_articles_and_videos, paginate_resources


class ArticlesTag(TaggedItemBase):
    content_object = ParentalKey(
        "Articles", on_delete=CASCADE, related_name="tagged_items"
    )


class Articles(BasePage):

    RESOURCES_PER_PAGE = 6

    # IMPORTANT: ARTICLES ARE NOW LABELLED "POSTS" IN THE FRONT END
    parent_page_types = ["home.HomePage"]
    subpage_types = ["Article"]
    template = "articles.html"

    class Meta:
        verbose_name = "posts"
        verbose_name_plural = "posts"

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

    # Meta fields
    keywords = ClusterTaggableManager(through=ArticlesTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [FieldPanel("description")]

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
                "Optional fields to override the default title "
                "and description for SEO purposes"
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

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    def get_context(self, request):
        context = super().get_context(request)
        context["filters"] = self.get_filters()
        context["resources"] = self.get_resources(request)
        return context

    def get_resources(self, request):
        # This Page class will show both Articles/Posts and Videos in its listing

        # We can't use __in in this deeply related query, so we have to make
        # a custom Q object instead and pass is in as a filter, then deal with
        # it later
        topics = request.GET.getlist(TOPIC_QUERYSTRING_KEY)
        topics_q = Q(topics__topic__slug__in=topics) if topics else Q()

        search_terms = request.GET.get(SEARCH_QUERYSTRING_KEY)

        resources = get_combined_articles_and_videos(
            self, q_object=topics_q, search_terms=search_terms
        )
        resources = paginate_resources(
            resources,
            page_ref=request.GET.get(PAGINATION_QUERYSTRING_KEY),
            per_page=self.RESOURCES_PER_PAGE,
        )

        return resources

    def get_filters(self):
        from ..topics.models import Topic

        return {
            "show_search_input": True,
            "topics": Topic.published_objects.order_by("title"),
        }


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey(
        "Article", on_delete=CASCADE, related_name="tagged_items"
    )


class ArticleTopic(Orderable):
    article = ParentalKey("Article", related_name="topics")
    topic = ForeignKey("topics.Topic", on_delete=CASCADE, related_name="+")

    panels = [PageChooserPanel("topic")]


class Article(BasePage):
    # IMPORTANT: EACH ARTICLE is NOW LABELLED "POST" IN THE FRONT END

    resource_type = "article"  # If you change this, CSS will need updating, too
    parent_page_types = ["Articles"]
    subpage_types = []
    template = "article.html"

    class Meta:
        verbose_name = "post"  # NB
        verbose_name_plural = "posts"  # NB

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
            "The main post content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        )
    )
    related_links = StreamField(
        StreamBlock([("link", ExternalLinkBlock())], required=False),
        blank=True,
        null=True,
        help_text="Optional links further reading",
        verbose_name="Related links",
    )

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
    date = DateField(
        "Post date",
        default=datetime.date.today,
        help_text="The date the post was published",
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
            "Optional list of the post's authors. Use ‘External author’ to add "
            "guest authors without creating a profile on the system"
        ),
    )
    keywords = ClusterTaggableManager(through=ArticleTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        StreamFieldPanel("body"),
        StreamFieldPanel("related_links"),
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
        FieldPanel("date"),
        StreamFieldPanel("authors"),
        MultiFieldPanel(
            [InlinePanel("topics")],
            heading="Topics",
            help_text=(
                "The topic pages this post will appear on. The first topic in the "
                "list will be treated as the primary topic and will be shown in the "
                "page’s related content."
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
        # Add FilterFields for things we may be filtering on (eg topics)
        index.FilterField("slug"),
    ]

    def get_absolute_url(self):
        # For the RSS feed
        return self.full_url

    @property
    def verbose_standfirst(self):
        """Return a marked-safe HTML snippet that can be used as a verbose standfirst"""

        template = "partials/verbose_standfirst.html"
        rendered = render_to_string(template, context={"page": self})
        return rendered

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the Article."""
        article_topic = self.topics.first()
        return article_topic.topic if article_topic else None

    @property
    def read_time(self):
        return str(readtime.of_html(str(self.body)))

    @property
    def related_resources(self):
        """Returns resources that are related to the current resource, i.e.
        live, public Articles and Videos which have the same Topics."""
        topic_pks = [topic.topic.pk for topic in self.topics.all()]
        return get_combined_articles_and_videos(self, topics__topic__pk__in=topic_pks)

    @property
    def month_group(self):
        return self.date.replace(day=1)

    def has_author(self, person):
        for author in self.authors:  # pylint: disable=not-an-iterable
            if author.block_type == "author" and str(author.value) == str(person.title):
                return True
        return False
