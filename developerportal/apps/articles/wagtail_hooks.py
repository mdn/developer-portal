from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from ..common.helpers import ExplorerRedirectAdminURLHelper
from .models import Articles


class ArticlesAdmin(ModelAdmin):
    model = Articles
    menu_icon = "doc-full-inverse"
    menu_order = 210
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(ArticlesAdmin)
