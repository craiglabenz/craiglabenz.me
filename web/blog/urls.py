# Django
from django.conf.urls import url
from django.views.generic import TemplateView

# Local
from blog import views

urlpatterns = [

    # Top-level page URLs
    url(r"^$", views.HomeView.as_view(), name="home"),
    url(r"^about/$", TemplateView.as_view(template_name='blog/about.html'), name="about"),
    url(r"^archive/$", views.ArchiveView.as_view(), name="archive"),

    # Entry URLs
    url(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$",
        views.EntryDetailView.as_view(), name="blog_entry_detail"),

    # Tag URLs
    url(r"^tags/(?P<tag_name>[-\w]+)/$", views.EntriesByTagView.as_view(), name="entries_by_tag"),
    url(r"^categories/(?P<slug>[-\w]+)/$", views.EntriesByCategoryView.as_view(), name="entries_by_category"),
]
