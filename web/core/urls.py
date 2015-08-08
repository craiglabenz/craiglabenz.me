# Django
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

# Local
from sitemap import CoreSitemap
from blog.sitemap import BlogSitemap


sitemaps = {
    'static': CoreSitemap,
    'blog': BlogSitemap
}


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    url(r'^', include('blog.urls')),
]


if settings.DEBUG:
    urlpatterns += [
        url(r'^404/$', TemplateView.as_view(template_name='404.html'), name="404"),
        url(r'^500/$', TemplateView.as_view(template_name='500.html'), name="500"),
    ]
