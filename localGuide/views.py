from django.shortcuts import redirect, render
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme

from Tourist.models import AssistanceRequest

from .forms import LoginForm, RegistrationForm
from .guide_forms import GuideAvailabilityForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('localGuide:login')
    else:
        form = RegistrationForm()

    return render(request, 'localGuide/register.html', {
        'title': 'Register',
        'form': form,
    })

def login(request):
    if request.user.is_authenticated:
        return redirect('localGuide:guide_dashboard')

    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('localGuide:guide_dashboard')
    else:
        form = LoginForm(request)

    return render(request, 'localGuide/login.html', {
        'title': 'Login',
        'form': form,
        'next': next_url,
    })


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('localGuide:login')


@login_required(login_url='localGuide:login')
def guide_dashboard(request):
    try:
        profile = request.user.profile
    except User.profile.RelatedObjectDoesNotExist:
        return redirect('localGuide:register')

    if request.method == 'POST':
        form = GuideAvailabilityForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('localGuide:guide_dashboard')
    else:
        form = GuideAvailabilityForm(instance=profile)

    open_requests = AssistanceRequest.objects.filter(status=AssistanceRequest.STATUS_OPEN)
    if profile.service_area:
        open_requests = open_requests.filter(area__iexact=profile.service_area)

    return render(request, 'localGuide/guide_dashboard.html', {
        'title': 'Local Guide Dashboard',
        'form': form,
        'open_requests': open_requests,
        'accepted_requests': AssistanceRequest.objects.filter(
            accepted_by=request.user,
            status=AssistanceRequest.STATUS_ACCEPTED,
        ),
    })


@login_required(login_url='localGuide:login')
def accept_assistance_request(request, request_id):
    if request.method != 'POST':
        return redirect('localGuide:guide_dashboard')

    try:
        profile = request.user.profile
    except User.profile.RelatedObjectDoesNotExist:
        return redirect('localGuide:register')

    if not profile.is_available:
        return redirect('localGuide:guide_dashboard')

    from django.db import transaction
    from django.utils import timezone

    with transaction.atomic():
        assistance_request = AssistanceRequest.objects.select_for_update().filter(
            pk=request_id,
            status=AssistanceRequest.STATUS_OPEN,
        ).first()
        if assistance_request is not None:
            if profile.service_area and assistance_request.area.lower() != profile.service_area.lower():
                return redirect('localGuide:guide_dashboard')
            assistance_request.status = AssistanceRequest.STATUS_ACCEPTED
            assistance_request.accepted_by = request.user
            assistance_request.accepted_at = timezone.now()
            assistance_request.save(update_fields=('status', 'accepted_by', 'accepted_at'))
            profile.is_available = False
            profile.save(update_fields=('is_available',))

    return redirect('localGuide:guide_dashboard')


@login_required(login_url='localGuide:login')
def complete_assistance_request(request, request_id):
    if request.method != 'POST':
        return redirect('localGuide:guide_dashboard')

    from django.utils import timezone

    assistance_request = AssistanceRequest.objects.filter(
        pk=request_id,
        accepted_by=request.user,
        status=AssistanceRequest.STATUS_ACCEPTED,
    ).first()
    if assistance_request is None:
        return redirect('localGuide:guide_dashboard')

    assistance_request.status = AssistanceRequest.STATUS_COMPLETED
    assistance_request.completed_at = timezone.now()
    assistance_request.save(update_fields=('status', 'completed_at'))

    profile = request.user.profile
    profile.is_available = True
    profile.save(update_fields=('is_available',))
    return redirect('localGuide:guide_dashboard')