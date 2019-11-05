from django import forms
from adminapp.models import Components
import re


class ComponentForm(forms.ModelForm):
    name = forms.CharField(label='name', min_length=3, max_length=100)
    static_description = forms.CharField(label='description', required=False, max_length=1000)
    parent_id = forms.IntegerField(label='parent', required=False)
    type = forms.CharField(label='type', required=False, max_length=255)
    building = forms.BooleanField(label='building', required=False)
    flat = forms.BooleanField(label='flat', required=False)

    class Meta:
        model = Components
        db_table = "components"
        fields = ('name', 'static_description', 'parent_id', 'type', 'building', 'flat')

    def clean(self):
        cleaned_data = super(ComponentForm, self).clean()
        # name = cleaned_data.get('name')
        # if Components.objects.filter(name=name).exclude(pk=self.instance.id).exists():
        #     self.add_error('name', 'Component is already exists.')

    def clean_type(self):
        data = self.cleaned_data['type']
        # do some stuff
        if data == '':
            data = None
        return data

    def save(self, request, commit=True):
        cleaned_data = super(ComponentForm, self).clean()
        obj = super(ComponentForm, self).save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.parent_id = cleaned_data.get('parent_id')
        obj.save()
        return obj

    def update(self, request, commit=True):
        cleaned_data = super(ComponentForm, self).clean()
        obj = super(ComponentForm, self).save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
        return obj

    def process(self):
        cd = self.cleaned_data
