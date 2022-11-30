from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm, PasswordChange


def pass_change_done(request):
    template = 'users/password_change_done.html'
    return render(request, template)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PassChange(CreateView):
    form_class = PasswordChange
    success_url = reverse_lazy('users:pass_change_done')
    teplate_name = 'users/password_change_form.html'
