from wagtail.core.models import BasePageManager, Page
from wagtail.core.query import PageQuerySet

from .forms import BasePageForm


class BasePublishedPageManager(BasePageManager):
    use_for_related_fields = True

    def get_queryset(self):
        return self._queryset_class(self.model).live().public().order_by("path")


PublishedPageManager = BasePublishedPageManager.from_queryset(PageQuerySet)


class BasePage(Page):
    base_form_class = BasePageForm
    published_objects = PublishedPageManager()

    class Meta:
        abstract = True
