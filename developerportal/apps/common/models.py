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

    class Meta:
        abstract = True
