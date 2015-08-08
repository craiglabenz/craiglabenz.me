# Django
from django.contrib.sitemaps import Sitemap

# Local Apps
from blog.models import Entry


class BlogSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Entry.objects.live()

    def lastmod(self, obj):
        return obj.updated_at or obj.published_on
