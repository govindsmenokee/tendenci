from django import forms
from django.utils.translation import ugettext_lazy as _
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.apps.tenants.models import Map, Kind, Tenant, Photo, Line


class MapForm(TendenciBaseForm):
    name = forms.CharField()
    status_detail = forms.ChoiceField(choices=(('active', 'Active'), ('pending', 'Pending')))

    class Meta:
        model = Map
        fields = (
            'name',
            'slug',
            'file',
            'description',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Map Information', {
                      'fields': ['name',
                                 'slug',
                                 'file',
                                 'description',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Image")


class TenantForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active', 'Active'), ('pending', 'Pending')))

    class Meta:
        model = Tenant
        fields = (
            'map',
            'name',
            'slug',
            'kind',
            'suite_number',
            'link',
            'phone',
            'hours_open',
            'description',
            'contact_info',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )
        widgets = {
          'map': forms.HiddenInput
        }

        fieldsets = [('Map Information', {
                      'fields': ['map',
                                 'name',
                                 'slug',
                                 'kind',
                                 'suite_number',
                                 'link',
                                 'phone',
                                 'hours_open',
                                 'description',
                                 'contact_info',
                                 'tags',
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(TenantForm, self).__init__(*args, **kwargs)
        self.fields['kind'].empty_label = None


class KindForm(forms.ModelForm):

    class Meta:
        model = Kind


class PhotoForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ('file',)


class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        exclude = ('tenant',)