from wagtail.contrib.modeladmin.options import modeladmin_register

from .models import Article
from ..common.helpers import ViewModelAdmin


class ArticleAdmin(ViewModelAdmin):
    model = Article
    menu_icon = 'doc-full'
    menu_order = 200
    list_display = ('title', 'date')
    list_filter = ('date',)
    list_sort = ('title', 'date')


modeladmin_register(ArticleAdmin)
