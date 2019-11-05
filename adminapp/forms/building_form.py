from django import forms
from adminapp.models import Buildings
import re


class BuildingForm(forms.ModelForm):
    hause_number = forms.CharField(required=True, max_length=45)
    display_number = forms.CharField(required=True, max_length=45)
    grundung = forms.CharField(required=False, max_length=45)
    aussenwande_eg_og_dg = forms.CharField(required=False, max_length=45)
    fenster_beschattung = forms.CharField(required=False, max_length=45)
    dach = forms.CharField(required=False, max_length=45)
    description = forms.CharField(required=False, max_length=1000)

    class Meta:
        model = Buildings
        fields = ('hause_number', 'display_number', 'description', 'grundung', 'aussenwande_eg_og_dg', 'fenster_beschattung', 'dach')

    def clean(self):
        cleaned_data = super(BuildingForm, self).clean()

    def save(self, request, commit=True):
        cleaned_data = super(BuildingForm, self).clean()
        obj = super(BuildingForm, self).save(commit=False)
        obj.project_id = request.project_id
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
        return obj

    def update(self, request, commit=True):
        cleaned_data = super(BuildingForm, self).clean()
        obj = super(BuildingForm, self).save(commit=False)
        obj.updated_by = request.user
        obj.save()
        return obj

    def process(self):
        cd = self.cleaned_data



