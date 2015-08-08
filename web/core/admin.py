# Django
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

# 3rd Party
from django_ace import AceWidget

# Local Apps
from .widgets import VerboseForeignKeyRawIdWidget

csrf_protect_m = method_decorator(csrf_protect)


class AceWidgetMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if getattr(settings, "USE_ACE_WIDGET", True):

            if db_field.name in ["body", "excerpt"]:
                kwargs["widget"] = AceWidget(mode=getattr(settings, "ACE_MODE", "markdown"),
                                             theme=getattr(settings, "ACE_THEME", "chrome"),
                                             width=getattr(settings, "ACE_WIDTH", "100%"),
                                             height=getattr(settings, "ACE_HEIGHT", "300px"))

            elif db_field.name == "code":
                kwargs["widget"] = AceWidget(mode=getattr(settings, "ACE_MODE", "text"),
                                             theme=getattr(settings, "ACE_THEME", "chrome"),
                                             width=getattr(settings, "ACE_WIDTH", "100%"),
                                             height=getattr(settings, "ACE_HEIGHT", "300px"))

        return super(AceWidgetMixin, self).formfield_for_dbfield(db_field, **kwargs)


class HyperlinkedRawIdAdminModel(admin.ModelAdmin):
    """
    Automatically replaces RawIdField widgets with HyperlinkedRawIdField widgets
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            type = db_field.rel.__class__.__name__
            if type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, admin.sites.site)
            return db_field.formfield(**kwargs)
        return super(HyperlinkedRawIdAdminModel, self).formfield_for_dbfield(db_field, **kwargs)


class BaseModelAdmin(HyperlinkedRawIdAdminModel, admin.ModelAdmin):

    additional_object_tool_excludes = ()
    change_form_template = 'core/admin/custom_change_form.html'
    change_list_template = 'core/admin/custom_change_list.html'

    @property
    def model_meta_info(self):
        return (self.model._meta.app_label, self.model._meta.model_name,)

    @property
    def admin_view_info(self):
        return '%s_%s' % self.model_meta_info

    @property
    def field_groups(self):
        field_groups = {
            '^': {
                'display_name': 'Starts With',
                'field_names': []
            },
            '=': {
                'display_name': 'Matches Exactly',
                'field_names': []
            },
            '*': {
                'display_name': 'Contains',
                'field_names': []
            }
        }

        for search_field in self.search_fields:
            if search_field.startswith('^'):
                field_groups['^']['field_names'].append(search_field[1:])
            elif search_field.startswith('='):
                field_groups['=']['field_names'].append(search_field[1:])
            else:
                field_groups['*']['field_names'].append(search_field)

        return field_groups

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj:
            context['additional_object_tools'] = self.additional_object_tools(obj)
        return super(BaseModelAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["additional_list_actions"] = self.additional_list_actions()
        return super(BaseModelAdmin, self).changelist_view(request, extra_context)

    def additional_list_actions(self):
        return []

    def additional_object_tools(self, obj):
        tool_urls = []
        excludes = self.get_additional_object_tool_excludes(obj)
        for relationship in obj._meta.get_all_related_objects():
            # Skip all excludes
            if relationship.get_accessor_name() in excludes:
                continue

            remote_field_name = relationship.field.name
            try:
                url = reverse('admin:%s_%s_changelist' % (relationship.model._meta.app_label, relationship.model._meta.model_name,))
                url += '?%s=%s' % (remote_field_name, obj.pk,)

                display_name = "View %s" % (relationship.get_accessor_name().title(),)
                display_name = display_name.replace('_', ' ')
                tool_urls.append({
                    'url': url,
                    'display_name': display_name
                })
            except NoReverseMatch:
                pass

        return tool_urls

    def get_additional_object_tool_excludes(self, obj):
        """
        Returns an interable of relationship ``get_accessor_name()`` values that should **not** be automatically
        added to the additional tools section in the admin.

        Generally speaking, ``get_accessor_name()`` returns the name of the ReverseManager,
        which is what is overwritten by the ``related_name`` keyword on ForeignKey fields.
        """
        return self.additional_object_tool_excludes
