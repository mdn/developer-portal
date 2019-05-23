from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Topic


class TopicAdmin(ModelAdmin):
    model = Topic
    menu_icon = 'tag'
    menu_order = 300
    list_display = ('title',)
    list_filter = ()
    list_sort = ('title',)


modeladmin_register(TopicAdmin)
