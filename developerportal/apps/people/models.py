import datetime
from itertools import chain
from operator import attrgetter

from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey,
    SET_NULL,
    TextField,
)
from django.forms import CheckboxSelectMultiple
from django.utils.text import slugify

from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase

from .edit_handlers import CustomLabelFieldPanel

from ..common.constants import ROLE_CHOICES


class PeopleTag(TaggedItemBase):
    content_object = ParentalKey('People', on_delete=CASCADE, related_name='tagged_items')


class People(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['Person']
    template = 'people.html'

    # Meta fields
    keywords = ClusterTaggableManager(through=PeopleTag, blank=True)

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    # Settings panels
    settings_panels = [
        FieldPanel('slug'),
        FieldPanel('show_in_menus'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    class Meta:
        verbose_name_plural = 'People'

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    def get_context(self, request):
        context = super().get_context(request)
        context['filters'] = self.get_filters()
        return context

    @property
    def people(self):
        return Person.objects.all().public().live().order_by('title')

    def get_filters(self):
        from ..topics.models import Topic
        return {
            'roles': True,
            'topics': Topic.objects.live().public().order_by('title'),
        }


class PersonTag(TaggedItemBase):
    content_object = ParentalKey('Person', on_delete=CASCADE, related_name='tagged_items')


class PersonTopic(Orderable):
    person = ParentalKey('Person', related_name='topics')
    topic = ForeignKey('topics.Topic', on_delete=CASCADE, related_name='+')

    panels = [
        PageChooserPanel('topic'),
    ]


class Person(Page):
    resource_type = 'person'
    parent_page_types = ['People']
    subpage_types = []
    template = 'person.html'

    # Content fields
    job_title = CharField(max_length=250)
    role = CharField(max_length=250, choices=ROLE_CHOICES, default='staff')
    description = RichTextField(default='', blank=True)
    image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )

    # Card fields
    card_title = CharField('Title', max_length=140, blank=True, default='')
    card_description = TextField('Description', max_length=140, blank=True, default='')
    card_image = ForeignKey(
        'mozimages.MozImage',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+',
        verbose_name='Image',
    )

    # Meta
    twitter = CharField(max_length=250, blank=True, default='')
    facebook = CharField(max_length=250, blank=True, default='')
    linkedin = CharField(max_length=250, blank=True, default='')
    github = CharField(max_length=250, blank=True, default='')
    email = CharField(max_length=250, blank=True, default='')
    keywords = ClusterTaggableManager(through=PersonTag, blank=True)

     # Content panels
    content_panels = [
        MultiFieldPanel([
            CustomLabelFieldPanel('title', label='Full name'),
            FieldPanel('job_title'),
            FieldPanel('role'),
        ], heading='About'),
        FieldPanel('description'),
        ImageChooserPanel('image'),
    ]

    # Card panels
    card_panels = [
        FieldPanel('card_title'),
        FieldPanel('card_description'),
        ImageChooserPanel('card_image'),
    ]

    # Meta panels
    meta_panels = [
        MultiFieldPanel([
            InlinePanel('topics'),
        ], heading='Topics interested in'),
        MultiFieldPanel([
            FieldPanel('twitter'),
            FieldPanel('facebook'),
            FieldPanel('linkedin'),
            FieldPanel('github'),
            FieldPanel('email'),
        ], heading='Profiles'),
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('keywords'),
        ], heading='SEO'),
    ]

    # Settings panels
    settings_panels = [
        FieldPanel('slug'),
    ]

    # Tabs
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(card_panels, heading='Card'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(settings_panels, heading='Settings', classname='settings'),
    ])

    @property
    def events(self):
        '''
        Return upcoming events where this person is a speaker,
        ordered by start date
        '''
        from ..events.models import Event

        upcoming_events = (Event
                .objects
                .filter(start_date__gte=datetime.datetime.now())
                .live()
                .public()
        )

        speaker_events = Event.objects.none()

        for event in upcoming_events.all():
            # add the event to the list if the current person is a speaker
            if event.has_speaker(self):
                speaker_events = speaker_events | Event.objects.page(event)

        return speaker_events.order_by('start_date')

    @property
    def articles(self):
        '''
        Return articles and external articles where this person is (one of) the authors,
        ordered by article date, most recent first
        '''
        from ..articles.models import Article
        from ..externalcontent.models import ExternalArticle

        articles = Article.objects.none()
        external_articles = ExternalArticle.objects.none()

        all_articles = Article.objects.live().public().all()
        all_external_articles = ExternalArticle.objects.live().public().all()

        for article in all_articles:
            if article.has_author(self):
                articles = articles | Article.objects.page(article)

        for external_article in all_external_articles:
            if external_article.has_author(self):
                external_articles = external_articles | ExternalArticle.objects.page(external_article)

        return sorted(chain(articles, external_articles), key=attrgetter('date'), reverse=True)

    @property
    def role_group(self):
        return {
            'slug': self.role,
            'title': dict(ROLE_CHOICES).get(self.role, ''),
        }
