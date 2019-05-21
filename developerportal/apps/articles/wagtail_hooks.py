from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Article


class ArticleAdmin(ModelAdmin):
    model = Article
    menu_icon = 'doc-full'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('title', 'date')
    list_filter = ('date',)
    list_sort = ('title', 'date')


modeladmin_register(ArticleAdmin)
