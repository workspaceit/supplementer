from django import forms
from adminapp.models import Flats


class FlatForm(forms.ModelForm):
    number = forms.CharField(required=True, max_length=45)
    description = forms.CharField(required=False, max_length=1000)
    client_name = forms.CharField(required=False, max_length=100)
    client_address = forms.CharField(required=False, max_length=1000)
    client_email = forms.CharField(required=False, max_length=50)
    client_tel = forms.CharField(required=False, max_length=50)

    class Meta:
        model = Flats
        fields = ('number', 'description', 'client_name', 'client_address', 'client_email', 'client_tel')

    def clean(self):
        cleaned_data = super(FlatForm, self).clean()

    def save(self, request, commit=True):
        cleaned_data = super(FlatForm, self).clean()
        obj = super(FlatForm, self).save(commit=False)
        obj.building_id = request.building_id
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
        return obj

    def update(self, request, commit=True):
        cleaned_data = super(FlatForm, self).clean()
        obj = super(FlatForm, self).save(commit=False)
        obj.updated_by = request.user
        obj.save()
        return obj

    def process(self):
        cd = self.cleaned_data



