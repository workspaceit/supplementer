from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render

class privacy_policy(View):
    def get(self, request):
        return render(request, 'misc_templates/privacy_policy.html')
