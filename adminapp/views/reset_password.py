from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages
from adminapp.models import ResetPassword
from adminapp.views.helper import LogHelper


class ResetPasswordRequestView(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'reset_password/request_reset_password.html', {})


class ResetPasswordView(TemplateView):

    def get(self, request, *args, **kwargs):
        hash_code = request.GET.get('key')
        try:
            reset_password = ResetPassword.objects.get(hash_code=hash_code)
            if datetime.now() > reset_password.expired_at:
                raise PasswordResetException("expired")
            elif reset_password.already_used:
                raise PasswordResetException("used")
            else:
                user = reset_password.user
                context = {'hash_code': hash_code, 'user_id': user.id}
                return render(request, 'reset_password/reset_password.html', context)
        except ObjectDoesNotExist:
            raise Http404("Key not exist")
        except PasswordResetException as e:
            LogHelper.elog(e)
            context = {}
            if e.message == 'expired':
                context = {'message': 'The link is already expired.'}
            elif e.message == 'used':
                context = {'message': 'The link is already used once by you.'}
            return render(request, 'reset_password/reset_password.html', context)

    def post(self, request, *args, **kwargs):
        try:
            hash_code = request.POST.get('key')
            user_id = request.POST.get('uid')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            reset_password = ResetPassword.objects.get(hash_code=hash_code, user__id=user_id)
            user = reset_password.user
            if datetime.now() > reset_password.expired_at:
                raise PasswordResetException("expired")
            elif reset_password.already_used:
                raise PasswordResetException("used")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                reset_password.already_used = True
                reset_password.save()
                messages.success(request, 'Your password is changed successfully. You can now login')
                return redirect('login')
            else:
                raise Exception
        except ObjectDoesNotExist:
            raise Http404()
        except PasswordResetException as e:
            LogHelper.elog(e)
            if e.message == 'expired':
                context = {'message': 'The link is already expired.'}
            elif e.message == 'used':
                context = {'message': 'The link is already used once by you.'}
            else:
                context = {'message': 'Something went wrong.'}
            return render(request, 'reset_password/reset_password.html', context)
        except Exception:
            LogHelper.elog('Something went wrong')
            messages.success(request, 'Something went wrong.')
            return redirect('login')


class PasswordResetException(Exception):
    def __init__(self, message):
        self.message = message




