from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import authenticate, login, logout


class LoginView(generic.DetailView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return render(request, 'profiles/login.html')

    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            user_data = {
                "id": user.id
            }
            request.session['is_logged_in'] = True
            request.session['supplementer_user'] = user_data
            request.session.modified = True
            return redirect('index')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'profiles/login.html', {'msg': 'Authenntication failed.Wrong Username or Password. Try Again'})


class LogoutView(generic.DetailView):
    def get(self, request):
        if 'active_project' in request.session:
            del request.session['active_project']
        if 'active_building' in request.session:
            del request.session['active_building']
        if 'active_flat' in request.session:
            del request.session['active_flat']
        logout(request)
        return redirect('login')



