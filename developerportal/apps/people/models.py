from django.forms import CheckboxSelectMultiple
from django.db.models import CharField, BooleanField, ForeignKey, SET_NULL
from django.utils.text import slugify
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from modelcluster.fields import ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager

class People(Page):
    subpage_types = ['Person']
    template = 'people.html'

class Person(Page):
    parent_page_types = ['People']
    subpage_types = []
    template = 'person.html'

    # Fields
    first_name = CharField(max_length=250)
    last_name = CharField(max_length=250)
    job_title = CharField(max_length=250)
    is_mozillian = BooleanField(default=True)
    profile_picture = ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    intro = RichTextField(default='')
    intro_image = ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name='+'
    )
    twitter = CharField(max_length=250, blank=True, default='')
    facebook = CharField(max_length=250, blank=True, default='')
    linkedin = CharField(max_length=250, blank=True, default='')
    github = CharField(max_length=250, blank=True, default='')
    email = CharField(max_length=250, blank=True, default='')
    labels = ParentalManyToManyField(
        'topics.Topic',
        blank=True,
        related_name='+',
        verbose_name='Topics interested in'
    )

    # Editor panel configuration
    content_panels = [
        FieldRowPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
          ]),
        FieldPanel('job_title'),
        FieldPanel('is_mozillian'),
        ImageChooserPanel('profile_picture'),
        FieldPanel('intro'),
        ImageChooserPanel('intro_image'),
        MultiFieldPanel([
            FieldPanel('twitter'),
            FieldPanel('facebook'),
            FieldPanel('linkedin'),
            FieldPanel('github'),
            FieldPanel('email'),
          ],
          heading='Profiles'),
        FieldPanel('labels', widget=CheckboxSelectMultiple),
    ]

    def clean(self):
        super().clean()
        derived_title = self.first_name + ' ' + self.last_name
        self.title = derived_title
        self.slug = slugify(derived_title)
