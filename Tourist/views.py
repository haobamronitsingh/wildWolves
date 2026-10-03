import logging
from decimal import Decimal, InvalidOperation

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from urllib.parse import urlencode

from .assistance_forms import AssistanceRequestForm
from .forms import TouristLoginForm, TouristRegistrationForm
from .models import AssistanceRequest, SOSAlert

from localGuide.models import UserProfile
from .services.sos import send_sos_sms

logger = logging.getLogger(__name__)


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
        dashboard_url = reverse('tourist:dashboard')
        query_string = request.GET.urlencode()
        if query_string:
            dashboard_url = f'{dashboard_url}?{query_string}'
        login_url = f"{reverse('tourist:login')}?{urlencode({'next': dashboard_url})}"
        return redirect(login_url)
    selected_area = request.GET.get('area', '').strip()
    if request.method == 'POST':
        form = AssistanceRequestForm(request.POST)
        if form.is_valid():
            assistance_request = form.save(commit=False)
            assistance_request.tourist = request.user
            assistance_request.save()
            return redirect('tourist:dashboard')
    else:
        form = AssistanceRequestForm(initial={'area': selected_area})

    requests = AssistanceRequest.objects.filter(tourist=request.user)
    return render(request, 'tourist/dashboard.html', {
        'title': 'Tourist Dashboard',
        'form': form,
        'requests': requests,
        'selected_area': selected_area,
    })


@require_POST
@login_required
def sos_alert(request):
    try:
        latitude = Decimal(request.POST.get('latitude', ''))
        longitude = Decimal(request.POST.get('longitude', ''))
    except (InvalidOperation, TypeError):
        return JsonResponse({'ok': False, 'error': 'A valid GPS location is required.'}, status=400)

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JsonResponse({'ok': False, 'error': 'The GPS coordinates are outside valid ranges.'}, status=400)

    alert = SOSAlert.objects.create(
        tourist=request.user,
        latitude=latitude,
        longitude=longitude,
    )
    guide_phones = list(
        UserProfile.objects.filter(is_available=True)
        .exclude(phone_number='')
        .values_list('phone_number', flat=True)
    )
    sms_result = send_sos_sms(alert, guide_phones)
    logger.info(
        "SOS alert %s recorded for %s; SMS status=%s; recipients=%d",
        alert.pk,
        request.user.username,
        sms_result,
        len(guide_phones),
    )
    return JsonResponse({
        'ok': True,
        'message': 'SOS alert recorded. SMS delivery requires an SMS provider configuration.',
        'recipient_count': len(guide_phones),
    })


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('tourist:login')
