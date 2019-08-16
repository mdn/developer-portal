from wagtail.contrib.modeladmin.options import modeladmin_register, ModelAdmin

from .models import Articles
from ..common.helpers import ExplorerRedirectAdminURLHelper


class ArticlesAdmin(ModelAdmin):
    model = Articles
    menu_icon = 'doc-full-inverse'
    menu_order = 210
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(ArticlesAdmin)
