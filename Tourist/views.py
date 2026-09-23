from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .assistance_forms import AssistanceRequestForm
from .forms import TouristLoginForm, TouristRegistrationForm
from .models import AssistanceRequest


def registerTourist(request):
    if request.user.is_authenticated:
        return redirect('tourist:dashboard')

    if request.method == 'POST':
        form = TouristRegistrationForm(request.POST)
        if form.is_valid():
            auth_login(request, form.save())
            return redirect('tourist:dashboard')
    else:
        form = TouristRegistrationForm()

    return render(request, 'tourist/register.html', {'title': 'Tourist Registration', 'form': form})


def loginTourist(request):
    if request.user.is_authenticated:
        return redirect('tourist:dashboard')

    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        form = TouristLoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('tourist:dashboard')
    else:
        form = TouristLoginForm(request)

    return render(request, 'tourist/login.html', {
        'title': 'Tourist Login',
        'form': form,
        'next': next_url,
    })


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('tourist:login')
    if request.method == 'POST':
        form = AssistanceRequestForm(request.POST)
        if form.is_valid():
            assistance_request = form.save(commit=False)
            assistance_request.tourist = request.user
            assistance_request.save()
            return redirect('tourist:dashboard')
    else:
        form = AssistanceRequestForm()

    requests = AssistanceRequest.objects.filter(tourist=request.user)
    return render(request, 'tourist/dashboard.html', {
        'title': 'Tourist Dashboard',
        'form': form,
        'requests': requests,
    })


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('tourist:login')
