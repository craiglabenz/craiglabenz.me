import collections

# Django
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView

# 3rd Party
from taggit.models import Tag

# Local
from blog.models import Category, Entry, TagColor


class EntryDetailView(TemplateView):
    template_name = 'blog/entry.html'

    def get_context_data(self, **kwargs):
        try:
            entry = Entry.objects.filter(slug=kwargs["slug"]).first()
        except Entry.DoesNotExist:
            raise Http404

        return {
            "entry": entry,
            "tag_colors": TagColor.objects.all(),
        }


class HomeView(TemplateView):
    template_name = "base.html"

    def get_entries_queryset(self):
        return Entry.objects.live().with_meta_data()

    def get_extra_context_data(self):
        return {}

    def get_context_data(self, **kwargs):
        context_data = {
            "entries": self.get_entries_queryset(),
            "tag_colors": TagColor.objects.all(),
        }
        context_data.update(self.get_extra_context_data())
        return context_data


class EntriesByTagView(HomeView):

    def get_entries_queryset(self):
        qs = super().get_entries_queryset()
        return qs.filter(tags__name__in=[self.kwargs["tag_name"]])

    def get_extra_context_data(self):
        return {
            'tag_name': self.kwargs['tag_name']
        }


class EntriesByCategoryView(HomeView):
    template_name = 'blog/categories.html'

    @property
    def category(self):
        if not hasattr(self, '_cat'):
            self._cat = get_object_or_404(Category, slug=self.kwargs["slug"])
        return self._cat

    def get_entries_queryset(self):
        return self.category.entries.live().with_meta_data()

    def get_extra_context_data(self):
        return {
            'category': self.category
        }


class ArchiveView(TemplateView):
    template_name = "blog/archive.html"

    def get_context_data(self):
        return {
            "tags": Tag.objects.all(),
            "tag_colors": TagColor.objects.all(),
            "categories": Category.objects.all(),
            "ordered_entries_by_month": self.get_ordered_entries()
        }

    def get_ordered_entries(self):
        ordered_entries_by_month = collections.OrderedDict()
        for entry in Entry.objects.live().with_meta_data():
            date_key = entry.published_on.strftime('%B %Y')
            if date_key not in ordered_entries_by_month:
                ordered_entries_by_month[date_key] = []

            ordered_entries_by_month[date_key].append(entry)

        return ordered_entries_by_month
