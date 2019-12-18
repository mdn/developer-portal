import logging

from django.db.utils import ProgrammingError
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.helpers import PageButtonHelper
from wagtail.contrib.modeladmin.helpers.url import AdminURLHelper
from wagtail.contrib.modeladmin.options import ModelAdmin

logger = logging.getLogger(__name__)


class ExplorerRedirectAdminURLHelper(AdminURLHelper):
    """Make the sidebar link for the particular page type go to the
    view of the page that lists their children, rather than the edit
    view of the top-level page itself (Articles, Events, Topics or Videos)

    eg: go to `/admin/pages/<id>/` rather than `/admin/videos/videos`
    """

    def _get_action_url_pattern(self, action):
        if action == "index" and self.model.objects:
            try:
                page = self.model.objects.first()
                if page:
                    return r"^pages/%s/$" % (page.pk)
                action = "add"
            except ProgrammingError as e:
                # Because Wagtail imports and executes this helper before
                # even `manage.py migrate` can run
                logger.exception(f"Temporarily ignoring exception: {e}")

        super()._get_action_url_pattern(action)


class ViewPageButtonHelper(PageButtonHelper):
    view_button_classnames = ["button-small"]

    def view_button(self, obj, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.view_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            "url": obj.url,
            "label": _("View live"),
            "classname": cn,
            "title": _("View live version of '%s'") % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, **kwargs):
        btns = [self.view_button(obj)]
        btns += super().get_buttons_for_obj(obj, **kwargs)
        return btns


class ViewModelAdmin(ModelAdmin):
    button_helper_class = ViewPageButtonHelper
