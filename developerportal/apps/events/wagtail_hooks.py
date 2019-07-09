from wagtail.contrib.modeladmin.options import modeladmin_register, ModelAdmin

from .models import Events
from ..common.helpers import ExplorerRedirectAdminURLHelper


class EventsAdmin(ModelAdmin):
    model = Events
    menu_icon = 'date'
    menu_order = 220
    url_helper_class = ExplorerRedirectAdminURLHelper

modeladmin_register(EventsAdmin)
