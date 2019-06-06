from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.helpers import PageButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin


class ViewPageButtonHelper(PageButtonHelper):
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
            'label': _('View live'),
            'classname': cn,
            'title': _("View live version of '%s'") % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, **kwargs):
        pk = getattr(obj, self.opts.pk.attname)
        btns = [
            self.view_button(obj),
        ]
        btns += super().get_buttons_for_obj(obj, **kwargs)
        return btns


class ViewModelAdmin(ModelAdmin):
    button_helper_class = ViewPageButtonHelper
