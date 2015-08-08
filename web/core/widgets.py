# Django
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.html import escape


# Via: https://gist.github.com/EmilStenstrom/4761449
class VerboseForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            change_url = reverse(
                "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.object_name.lower()),
                args=(obj.pk,)
            )
            return '&nbsp;<strong><a href="%s">%s</a></strong>' % (change_url, escape(obj))
        except (ValueError, self.rel.to.DoesNotExist):
            return '???'
        except NoReverseMatch:
            return super(VerboseForeignKeyRawIdWidget, self).label_for_value(value)
