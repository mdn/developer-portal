from django.contrib import admin

from .models import IngestionConfiguration


class IngestionConfigAdmin(admin.ModelAdmin):
    model = IngestionConfiguration


admin.site.register(IngestionConfiguration, IngestionConfigAdmin)
