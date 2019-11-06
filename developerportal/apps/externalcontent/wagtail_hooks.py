from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.helpers import PageButtonHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import ExternalArticle, ExternalContent, ExternalEvent, ExternalVideo


class ExternalContentButtonHelper(PageButtonHelper):
    parent_page_types = []
    subpage_types = []
    view_button_classnames = ["button-small"]

    def view_button(self, obj, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.view_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            "url": obj.external_url,
            "label": _("View external link"),
            "classname": cn,
            "title": _("View external link: %s") % obj.external_url,
        }

    def get_buttons_for_obj(self, obj, **kwargs):
        btns = super().get_buttons_for_obj(obj, **kwargs)
        btns.append(self.view_button(obj))
        return btns


class BaseExternalEntityAdmin(ModelAdmin):
    """We want all the ExternalContent Pages to show in the list,
    not just the live ones. And we want to make it easy to see which
    of them is live and which is draft."""

    list_display = ("title", "show_draft_status")

    def show_draft_status(self, obj):
        if obj.live:
            return "Published"
        else:
            return "Draft"

    show_draft_status.short_description = "Published state?"

    def get_queryset(self, request):
        # super().get_queryset() uses the default manager, which only gets
        # live Pages, but here we want to see drafts, too
        qs = self.model.objects.all()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class ExternalContentAdmin(BaseExternalEntityAdmin):
    model = ExternalContent
    menu_icon = "link"
    menu_label = "All content"
    exclude_from_explorer = True
    button_helper_class = ExternalContentButtonHelper


class ExternalArticleAdmin(BaseExternalEntityAdmin):
    model = ExternalArticle
    menu_icon = "doc-full-inverse"
    menu_label = "Posts"
    exclude_from_explorer = True
    button_helper_class = ExternalContentButtonHelper


class ExternalEventAdmin(BaseExternalEntityAdmin):
    model = ExternalEvent
    menu_icon = "date"
    menu_label = "Events"
    exclude_from_explorer = True
    button_helper_class = ExternalContentButtonHelper


class ExternalVideoAdmin(BaseExternalEntityAdmin):
    model = ExternalVideo
    menu_icon = "media"
    menu_label = "Videos"
    exclude_from_explorer = True
    button_helper_class = ExternalContentButtonHelper


class ExternalContentAdminGroup(ModelAdminGroup):
    menu_label = "External content"
    menu_icon = "folder-open-inverse"
    menu_order = 250
    items = (
        ExternalContentAdmin,
        ExternalArticleAdmin,
        ExternalEventAdmin,
        ExternalVideoAdmin,
    )


modeladmin_register(ExternalContentAdminGroup)
