from django import forms
from adminapp.models import Users, ProjectStuff
import re


class ProfileForm(forms.ModelForm):
    username = forms.CharField(required=True, max_length=45)
    first_name = forms.CharField(required=False, max_length=45)
    last_name = forms.CharField(required=False, max_length=45)
    email = forms.CharField(required=True, max_length=45)
    avatar = forms.FileField(required=False)
    address = forms.CharField(required=False, max_length=1000)
    is_active = forms.CharField(required=False, max_length=1)

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'address', 'avatar')

        def clean(self):
            cleaned_data = super(ProfileForm, self).clean()
            if Users.objects.filter(email=cleaned_data.get("email")).exclude(pk=self.instance.id).exists():
                self.add_error('email', 'A user with that email already exists')


class UserForm(ProfileForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=True)
    project_list = forms.CharField(required=False, max_length=1000)

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'is_active', 'address', 'avatar', 'project_list')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if Users.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', 'A user with that email already exists.')

    def save(self, request, commit=False):
        # cleaned_data = super(ProfileForm, self).clean()
        obj = super(UserForm, self).save(commit=False)
        obj.is_active = "1"
        obj.is_staff = "1"
        obj.set_password(self.cleaned_data['password'])
        obj.save()
        return obj


class UserUpdateForm(ProfileForm):

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'avatar')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        if Users.objects.filter(email=cleaned_data.get("email")).exclude(pk=self.instance.id).exists():
            self.add_error('email', 'A user with that email already exists.')
        if cleaned_data.get("avatar") != self.instance.avatar:
            self.instance.avatar.delete(save=False)

    def update(self, request, commit=True):
        obj = super(ProfileForm, self).save(commit=False)
        obj.save()
        return obj


class WorkerForm(ProfileForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=True)
    telephone_office = forms.CharField(required=False, max_length=45)
    telephone_mobile = forms.CharField(required=False, max_length=45)
    company_name = forms.CharField(required=True, max_length=100)
    working_type = forms.CharField(required=True, max_length=1000)

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'is_active', 'address', 'avatar', 'working_type')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if Users.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', 'A user with that email already exists.')

    def save(self, request, commit=False):
        # cleaned_data = super(ProfileForm, self).clean()
        obj = super(WorkerForm, self).save(commit=False)
        obj.is_active = "1"
        obj.is_staff = "0"
        obj.set_password(self.cleaned_data['password'])
        obj.save()
        return obj


class WorkerUpdateForm(ProfileForm):
    telephone_office = forms.CharField(required=False, max_length=45)
    telephone_mobile = forms.CharField(required=False, max_length=45)
    company_name = forms.CharField(required=True, max_length=100)
    working_type = forms.CharField(required=True, max_length=1000)

    class Meta:
        model = Users
        fields = ('username', 'first_name', 'last_name', 'email', 'address', 'avatar')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        if Users.objects.filter(email=cleaned_data.get("email")).exclude(pk=self.instance.id).exists():
            self.add_error('email', 'A user with that email already exists.')
        if cleaned_data.get("avatar") != self.instance.avatar:
            self.instance.avatar.delete(save=False)

    def update(self, request, commit=True):
        obj = super(ProfileForm, self).save(commit=False)
        obj.save()
        return obj


class UserPasswordChangeForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(), max_length=200, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ('password',)

    def clean(self):
        cleaned_data = super(UserPasswordChangeForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

    def save(self, request, commit=False):
        obj = super(UserPasswordChangeForm, self).save(commit=False)
        obj.set_password(self.cleaned_data['password'])
        obj.save()
        return obj

