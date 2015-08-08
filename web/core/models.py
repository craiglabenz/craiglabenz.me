import inspect

# Django
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

# Local
from .utils import site_url


class BaseModel(models.Model):

    # Bookkeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    serialization_excludes = ["created_at", "updated_at"]

    class Meta:
        abstract = True

    def __str__(self):
        try:
            return self.as_str()
        except:
            return '%s Id: %s' % (self._meta.verbose_name, self.pk,)

    def as_str(self):
        """
        Classes extending BaseModel are encouraged to implement ``as_str``
        instead of ``__str__`` to prevent any accidental data mismatching
        from ever breaking production functionality.
        """
        return self.name

    @property
    def meta_info(self):
        return (self._meta.app_label, self._meta.model_name,)

    @property
    def admin_view_info(self):
        return '%s_%s' % self.meta_info

    @property
    def admin_uri(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name,), args=(self.pk,))

    @property
    def admin_url(self):
        return site_url(uri=self.admin_uri)

    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def field_names(cls):
        """
        Returns the names of all fields on the model
        """
        return [field.name for field in cls._meta.fields]

    def finalize_serialization(self, serialized, strip_empty=False, **kwargs):
        """
        A hook for child classes to do more phun stuff.
        """
        if strip_empty:
            for key, value in serialized.items():
                if value is None or (isinstance(value, dict) and value['id'] is None):
                    serialized.pop(key)
        return serialized

    def get_serialization_excludes(self):
        return self.serialization_excludes

    def serialize(self, full=False, id_nested=False, strip_empty=False, excludes=[]):
        """
        Returns a dictionary of all local fields.
        """
        excludes = self.get_serialization_excludes() + excludes

        serialized = {field.name: self.get_field_value(field.name, full) for field in self.__class__._meta.fields if field.name not in excludes}
        serialized.update(self.get_serialized_extras(excludes))
        return self.finalize_serialization(serialized, strip_empty=strip_empty, excludes=excludes)

    def get_serialized_extras(self, excludes=[]):
        """
        Loops over dir(self) and finds all attrs of the format ``serialize_{0}``
        and attaches their result to the key ``{0}``
        """
        data = {}
        for key in dir(self):
            if key in excludes:
                continue

            if key.startswith("serialize_"):
                new_key = key[10:]
                value = getattr(self, key, None)

                # If the thing is a callable... call it.
                if inspect.isfunction(value) or inspect.ismethod(value):
                    value = value()

                data[new_key] = value

        return data

    def reload(self):
        """
        In place DB update of the record.
        """
        new_self = self.__class__.objects.get(pk=self.pk)
        self.__dict__.update(new_self.__dict__)
        return self

    def get_field_value(self, field_name, full=False):
        """
        Returns a given value of for this instantiated model.

        Arguments:
        field_name    {string}      The value of the attr you want
        full          {bool}        OPTIONAL. If the passed name is a relation, should it be hydrated?
                                    Defaults to False.
        """
        field = self._meta.get_field(field_name)
        # Is this a related field or a literal?
        if isinstance(field, models.fields.related.RelatedField):
            if full:
                # It's related and they ordered it hydrated
                val = getattr(self, field_name, None)
                # Pull out the value and hydrate it if it exists, else
                # return None
                if val is not None:
                    return val.serialize()  # Don't forward `full` to avoid cyclical problems
                else:
                    return None
            else:
                # Not hydrated is easy enough, just return the PK we
                # already have on hand
                _id = getattr(self, '%s_id' % (field_name,), None)
                serialized = {'id': _id}

                if hasattr(field.related_model, 'add_to_serialization_as_relation'):
                    obj = getattr(self, field.name)
                    if obj:
                        serialized.update(obj.add_to_serialization_as_relation())

                return serialized
                # return _id
        elif isinstance(field, models.fields.DateField):  # Covers both DateTimeField and DateField
            return self._meta.get_field(field_name).value_to_string(self)
        else:
            # Not related? Too easy.
            return getattr(self, field_name, None)
