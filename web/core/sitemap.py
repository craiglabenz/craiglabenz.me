# Django
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class CoreSitemap(Sitemap):
    changefeq = "weekly"
    priority = 0.5

    def items(self):
        return ['home', 'about', 'archive']

    def location(self, item):
        return reverse(item)
