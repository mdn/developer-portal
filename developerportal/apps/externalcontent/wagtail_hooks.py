from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.helpers import PageButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import ExternalContent


class ExternalContentButtonHelper(PageButtonHelper):
    view_button_classnames = ['button-small']

    def view_button(self, obj, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.view_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': obj.url,
            'label': _('View external link'),
            'classname': cn,
            'title': _("View external link: %s") % obj.external_url,
        }

    def get_buttons_for_obj(self, obj, **kwargs):
        btns = super().get_buttons_for_obj(obj, **kwargs)
        btns.append(self.view_button(obj))
        return btns


class ExternalContentAdmin(ModelAdmin):
    model = ExternalContent
    menu_icon = 'link'
    menu_label = 'External Links'
    menu_order = 300
    button_helper_class = ExternalContentButtonHelper


modeladmin_register(ExternalContentAdmin)
