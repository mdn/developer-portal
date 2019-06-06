from wagtail.contrib.modeladmin.options import modeladmin_register

from .models import Topic
from ..common.helpers import ViewModelAdmin


class TopicAdmin(ViewModelAdmin):
    model = Topic
    menu_icon = 'tag'
    menu_order = 300
    list_display = ('title',)
    list_filter = ()
    list_sort = ('title',)


modeladmin_register(TopicAdmin)
