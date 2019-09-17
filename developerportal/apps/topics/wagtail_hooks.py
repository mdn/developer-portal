from wagtail.contrib.modeladmin.options import modeladmin_register, ModelAdmin

from .models import Topics
from ..common.helpers import ExplorerRedirectAdminURLHelper


class TopicsAdmin(ModelAdmin):
    model = Topics
    menu_icon = "tag"
    menu_order = 200
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(TopicsAdmin)
