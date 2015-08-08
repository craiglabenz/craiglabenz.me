# Django
from django.db.models import QuerySet


class EntryQuerySet(QuerySet):

    def live(self):
        return self.filter(status=self.model.LIVE)

    def with_meta_data(self):
        return self.prefetch_related("tags").order_by("-published_on", "-pk")
