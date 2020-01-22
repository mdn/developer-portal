from django.core.cache import cache
from django.db import transaction
from django.db.models import SET_NULL, ForeignKey

from wagtail.core.models import Page, PageManager

from .forms import BasePageForm


class PublishedPageManager(PageManager):
    def get_queryset(self):
        # This method restricts queries to live (non-draft) pages. It doesn't
        # guard against private pages (i.e. using `.public()`) because this
        # causes initial migrations to fail, however private aren't supported
        # by the static site build.
        return super().get_queryset().live()


class BasePage(Page):
    base_form_class = BasePageForm
    published_objects = PublishedPageManager()

    social_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
    )

    #  A single place to store/define cache keys that need invalidation
    # when the object is saved
    _bulk_invalidation_cache_keys = []

    class Meta:
        abstract = True

    @transaction.atomic()
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete_many(self._bulk_invalidation_cache_keys)
