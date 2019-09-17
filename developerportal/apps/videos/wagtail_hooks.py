from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from ..common.helpers import ExplorerRedirectAdminURLHelper
from .models import Videos


class VideosAdmin(ModelAdmin):
    model = Videos
    menu_icon = "media"
    menu_order = 240
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(VideosAdmin)
