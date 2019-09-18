from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from ..common.helpers import ExplorerRedirectAdminURLHelper
from .models import Events


class EventsAdmin(ModelAdmin):
    model = Events
    menu_icon = "date"
    menu_order = 220
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(EventsAdmin)
