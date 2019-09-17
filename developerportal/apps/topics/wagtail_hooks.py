from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from ..common.helpers import ExplorerRedirectAdminURLHelper
from .models import Topics


class TopicsAdmin(ModelAdmin):
    model = Topics
    menu_icon = "tag"
    menu_order = 200
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(TopicsAdmin)
