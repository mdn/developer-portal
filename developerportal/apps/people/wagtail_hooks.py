from wagtail.contrib.modeladmin.options import modeladmin_register, ModelAdmin

from .models import People
from ..common.helpers import ExplorerRedirectAdminURLHelper


class PeopleAdmin(ModelAdmin):
    model = People
    menu_icon = 'group'
    menu_order = 230
    url_helper_class = ExplorerRedirectAdminURLHelper


modeladmin_register(PeopleAdmin)
