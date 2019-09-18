from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from ..common.helpers import ExplorerRedirectAdminURLHelper
from .models import People


class PeopleAdmin(ModelAdmin):
    model = People
    menu_icon = "group"
    menu_order = 230
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(PeopleAdmin)
