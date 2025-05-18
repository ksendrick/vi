from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login as auth_login

from authapp.forms import LoginForm, RegisterForm


def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)

            if user.is_superuser:
                return HttpResponseRedirect('/admin/')
            elif user.is_staff:
                return HttpResponseRedirect(reverse('staffadmin:newsapp_news_changelist'))
            else:
                return HttpResponseRedirect(reverse('mainapp:index'))
    else:
        form = LoginForm()

    context = {
        'title': 'Авторизация',
        'form': form
    }
    return render(request, 'authapp/login.html', context)

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('mainapp:index'))


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('authapp:confirm_email')
    else:
        form = RegisterForm()

    context = {
        'title': 'регистрация',
        'form': form
    }
    return render(request, 'authapp/register.html', context)


@login_required
def confirm_email(request):
    error = None

    if request.method == 'POST':
        entered_code = request.POST.get('confirmation_code')
        if entered_code == request.user.email_confirmation_code:
            request.user.email_confirmed = True
            request.user.save()
            return redirect('mainapp:index')
        else:
            error = 'Неверный код'

    return render(request, 'authapp/confirmation.html', {'error': error, 'title': 'Подтверждение пароля'})