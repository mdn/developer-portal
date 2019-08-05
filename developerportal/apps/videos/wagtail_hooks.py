from wagtail.contrib.modeladmin.options import modeladmin_register, ModelAdmin

from .models import Videos
from ..common.helpers import ExplorerRedirectAdminURLHelper


class VideosAdmin(ModelAdmin):
    model = Videos
    menu_icon = 'media'
    menu_order = 250
    url_helper_class = ExplorerRedirectAdminURLHelper

modeladmin_register(VideosAdmin)
