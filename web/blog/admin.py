# Django
from django.contrib import admin

# Local Apps
from core.admin import AceWidgetMixin, BaseModelAdmin
from blog.models import Entry, Category, Snippet, Language, TagColor


class CategoryAdmin(BaseModelAdmin):
    pass


class LanguageAdmin(BaseModelAdmin):
    pass


class SnippetAdmin(BaseModelAdmin):
    prepopulated_fields = {"slug": ["title"]}


class SnippetInline(admin.StackedInline):
    model = Snippet
    prepopulated_fields = {"slug": ["title"]}
    extra = 0


class EntryAdmin(AceWidgetMixin, BaseModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    inlines = [SnippetInline]


class TagColorAdmin(BaseModelAdmin):
    pass


admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(TagColor, TagColorAdmin)
