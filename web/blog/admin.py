# Django
from django.contrib import admin

# Local Apps
from core.admin import AceWidgetMixin, BaseModelAdmin
from blog.models import Entry, Category, TagColor


class CategoryAdmin(BaseModelAdmin):
    pass


class LanguageAdmin(BaseModelAdmin):
    pass


class SnippetAdmin(BaseModelAdmin):
    prepopulated_fields = {"slug": ["title"]}


class EntryAdmin(AceWidgetMixin, BaseModelAdmin):
    prepopulated_fields = {"slug": ["title"]}


class TagColorAdmin(BaseModelAdmin):
    pass


admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TagColor, TagColorAdmin)
