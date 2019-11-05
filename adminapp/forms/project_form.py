from django import forms
from adminapp.models import Projects
import re


class ProjectForm(forms.ModelForm):
    name = forms.CharField(required=True, max_length=200)
    address = forms.CharField(required=False, max_length=1000)
    description = forms.CharField(required=False, max_length=1000)
    type = forms.CharField(required=False, max_length=100)
    city = forms.CharField(required=False, max_length=100)
    energetic_standard = forms.CharField(required=False, max_length=100)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = Projects
        fields = ('name', 'address', 'description', 'type', 'city', 'energetic_standard', 'start_date', 'end_date')

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        name = cleaned_data.get('name')
        if Projects.objects.filter(name=name).exclude(pk=self.instance.id).exists():
            self.add_error('name', 'Project name is already exists.')

    def save(self, request, commit=True):
        cleaned_data = super(ProjectForm, self).clean()
        obj = super(ProjectForm, self).save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
        return obj

    def update(self, request, commit=True):
        cleaned_data = super(ProjectForm, self).clean()
        obj = super(ProjectForm, self).save(commit=False)
        obj.updated_by = request.user
        obj.save()
        return obj

    def process(self):
        cd = self.cleaned_data



