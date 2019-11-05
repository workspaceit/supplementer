from django.urls import reverse_lazy
from django.views.generic import UpdateView
from adminapp.models import Users
from adminapp.forms.user_form import ProfileForm
from django.shortcuts import render, redirect
from django.views import generic
from adminapp.views.helper import LogHelper
from django.contrib.auth import update_session_auth_hash


class ProfileUpdateView(UpdateView):

    model = Users
    form_class = ProfileForm
    template_name = 'profiles/profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile-update')

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        context['avatar'] = self.object.avatar.url if self.object.avatar else ''
        return context


class ChangePassword(generic.DetailView):
    def get(self,request):
        return render(request, 'profiles/change_password.html')

    def post(self,request):
        try:
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            user = Users.objects.get(id=request.user.id)
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('index')
            else:
                return render(request, 'profiles/change_password.html', {'msg': 'Password is not Correct. Try Again'})
        except Exception as e:
            LogHelper.elog(e)
            return render(request, 'profiles/change_password.html', {'msg': 'Something went wrong. Please Try Again'})
