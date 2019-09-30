from wagtail.core.models import PageManager, Page

from .forms import BasePageForm


class PublishedPageManager(PageManager):
    def get_queryset(self):
        # This method restricts the query to only live (non-draft) pages - it
        # doesn't guard against private pages, however these aren't supported
        # by the static site build.
        return super().get_queryset().live()


class BasePage(Page):
    base_form_class = BasePageForm
    published_objects = PublishedPageManager()

    class Meta:
        abstract = True
