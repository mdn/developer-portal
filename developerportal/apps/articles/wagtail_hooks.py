from wagtail.contrib.modeladmin.options import modeladmin_register

from .models import Article
from ..common.helpers import ViewModelAdmin


class ArticleAdmin(ViewModelAdmin):
    model = Article
    menu_icon = 'doc-full'
    menu_order = 200
    list_display = ('title', 'authors', 'date')
    list_filter = ('date',)
    list_sort = ('title', 'date')

    def authors(self, obj):
        article_authors = obj.authors.all()
        return [author.author for author in article_authors]

modeladmin_register(ArticleAdmin)
