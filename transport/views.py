import json
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import LocalRouteForm, RegisterForm, RentalInquiryForm, StyledAuthForm
from .models import LocalRoute, RentalInquiry, RentalVehicle, RideInvite, TravelSession, UserProfile

TRENDING_PLACES = [
    {
        "name": "Loktak Lake",
        "location": "Bishnupur, Manipur",
        "category": "Nature and water",
        "description": "Explore floating phumdis, peaceful waters, and the famous Sendra viewpoint.",
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=85",
        "score": 98,
    },
    {
        "name": "Kangla Fort",
        "location": "Imphal West, Manipur",
        "category": "Heritage",
        "description": "Walk through the historic heart of Manipur and discover stories of its royal past.",
        "image": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=900&q=85",
        "score": 94,
    },
    {
        "name": "Shirui Hills",
        "location": "Ukhrul, Manipur",
        "category": "Hills and trekking",
        "description": "Breathe in mountain air and follow trails through the home of the rare Shirui Lily.",
        "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=85",
        "score": 91,
    },
]


def home(request):
    return render(
        request,
        "home.html",
        {"trending_place": TRENDING_PLACES[0], "trending_places": TRENDING_PLACES},
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("transport:hub")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to WildWolves transportation.")
        return redirect("transport:hub")
    return render(request, "auth.html", {"form": form, "mode": "register", "title": "Register"})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("transport:hub")
    form = StyledAuthForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "transport:hub")
    return render(request, "auth.html", {"form": form, "mode": "login", "title": "Log in"})


def logout_view(request):
    logout(request)
    return redirect("home")


def _feature_context(active):
    return {"active_feature": active}


def transport_hub(request):
    return redirect("transport:ride")


@login_required
def ride_share(request):
    session = TravelSession.objects.filter(user=request.user).first()
    incoming = RideInvite.objects.filter(to_user=request.user, status=RideInvite.PENDING)
    accepted = RideInvite.objects.filter(status=RideInvite.ACCEPTED).filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    )
    return render(
        request,
        "transport/ride.html",
        {
            **_feature_context("ride"),
            "session": session,
            "incoming": incoming,
            "accepted": accepted,
            "radius": settings.NEARBY_RADIUS_METERS,
            "has_location": session is not None and session.lat is not None,
        },
    )


@login_required
@require_POST
def update_presence(request):
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    destination = (payload.get("destination") or "").strip()
    if not destination:
        return JsonResponse({"ok": False, "error": "Enter a destination."}, status=400)

    def as_float(value):
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    session, _ = TravelSession.objects.update_or_create(
        user=request.user,
        defaults={
            "destination": destination,
            "dest_lat": as_float(payload.get("dest_lat")),
            "dest_lng": as_float(payload.get("dest_lng")),
            "lat": as_float(payload.get("lat")),
            "lng": as_float(payload.get("lng")),
            "open_to_share": bool(payload.get("open_to_share")),
        },
    )
    return JsonResponse({"ok": True, "updated_at": session.updated_at.isoformat()})


@login_required
def nearby_travelers(request):
    session = TravelSession.objects.filter(user=request.user).first()
    if not session:
        return JsonResponse({"ok": True, "people": [], "message": "Share your destination first."})

    cutoff = timezone.now() - timedelta(seconds=settings.PRESENCE_STALE_SECONDS)
    people = []
    others = TravelSession.objects.select_related("user", "user__transport_profile").exclude(
        user=request.user
    ).filter(updated_at__gte=cutoff, open_to_share=True)
    for other in others:
        if not session.same_destination(other):
            continue
        distance = session.distance_to(other) if session.lat is not None else None
        if session.lat is not None and (distance is None or distance > settings.NEARBY_RADIUS_METERS):
            continue
        invite = (
            RideInvite.objects.filter(from_user=request.user, to_user=other.user)
            .order_by("-created_at")
            .first()
        )
        reverse = (
            RideInvite.objects.filter(from_user=other.user, to_user=request.user, status=RideInvite.PENDING)
            .order_by("-created_at")
            .first()
        )
        phone = ""
        if invite and invite.status == RideInvite.ACCEPTED:
            phone = getattr(getattr(other.user, "transport_profile", None), "phone_number", "") or ""
        people.append(
            {
                "id": other.user_id,
                "username": other.user.username,
                "destination": other.destination,
                "distance_m": round(distance) if distance is not None else None,
                "open_to_share": other.open_to_share,
                "lat": other.lat,
                "lng": other.lng,
                "invite_status": invite.status if invite else None,
                "incoming_invite_id": reverse.id if reverse else None,
                "phone": phone,
            }
        )
    people.sort(key=lambda item: item["distance_m"])
    return JsonResponse({"ok": True, "people": people, "self": {"lat": session.lat, "lng": session.lng, "destination": session.destination}})


@login_required
@require_POST
def send_ride_invite(request):
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    to_id = payload.get("user_id")
    try:
        to_id = int(to_id)
    except (TypeError, ValueError):
        to_id = None
    if not to_id or to_id == request.user.id:
        return JsonResponse({"ok": False, "error": "Choose a nearby traveler."}, status=400)
    session = TravelSession.objects.filter(user=request.user).first()
    other = get_object_or_404(TravelSession, user_id=to_id)
    if not session or not session.same_destination(other):
        return JsonResponse({"ok": False, "error": "You are not heading to the same destination."}, status=400)
    if not other.open_to_share:
        return JsonResponse({"ok": False, "error": "This traveler has not opted in to share a ride."}, status=400)

    invite, created = RideInvite.objects.get_or_create(
        from_user=request.user,
        to_user=other.user,
        status=RideInvite.PENDING,
        defaults={"destination": session.destination},
    )
    if not created:
        return JsonResponse({"ok": True, "status": invite.status, "message": "Invite already sent."})
    return JsonResponse({"ok": True, "status": invite.status, "id": invite.id})


@login_required
@require_POST
def respond_ride_invite(request, invite_id):
    invite = get_object_or_404(RideInvite, id=invite_id, to_user=request.user, status=RideInvite.PENDING)
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        payload = {}
    answer = (payload.get("answer") or request.POST.get("answer") or "").lower()
    if answer not in {"yes", "no"}:
        return JsonResponse({"ok": False, "error": "Choose yes or no."}, status=400)
    invite.status = RideInvite.ACCEPTED if answer == "yes" else RideInvite.DECLINED
    invite.responded_at = timezone.now()
    invite.save(update_fields=["status", "responded_at"])
    phone = ""
    if invite.status == RideInvite.ACCEPTED:
        phone = getattr(getattr(invite.from_user, "transport_profile", None), "phone_number", "") or ""
    if request.headers.get("HX-Request") or request.content_type == "application/json" or request.headers.get("Accept", "").find("application/json") >= 0:
        return JsonResponse({"ok": True, "status": invite.status, "phone": phone})
    messages.success(request, f"You answered {answer} to {invite.from_user.username}.")
    return redirect("transport:ride")


def local_routes(request):
    routes = LocalRoute.objects.filter(is_active=True)
    mode = request.GET.get("mode")
    if mode in {LocalRoute.BUS, LocalRoute.AUTO}:
        routes = routes.filter(mode=mode)
    form = LocalRouteForm() if request.user.is_authenticated and request.user.is_staff else None
    return render(
        request,
        "transport/local.html",
        {**_feature_context("local"), "routes": routes, "form": form, "mode": mode or "all"},
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def add_local_route(request):
    form = LocalRouteForm(request.POST)
    if form.is_valid():
        route = form.save(commit=False)
        route.created_by = request.user
        route.save()
        messages.success(request, "Route published for travelers.")
        return redirect("transport:local")
    routes = LocalRoute.objects.filter(is_active=True)
    messages.error(request, "Please correct the route form.")
    return render(
        request,
        "transport/local.html",
        {**_feature_context("local"), "routes": routes, "form": form, "mode": "all"},
        status=400,
    )


def private_transport(request):
    two = RentalVehicle.objects.filter(kind=RentalVehicle.TWO, available=True)
    four = RentalVehicle.objects.filter(kind=RentalVehicle.FOUR, available=True)
    form = RentalInquiryForm()
    my_rentals = []
    if request.user.is_authenticated:
        my_rentals = RentalInquiry.objects.filter(user=request.user).select_related("vehicle")[:8]
    return render(
        request,
        "transport/private.html",
        {
            **_feature_context("private"),
            "two_wheelers": two,
            "four_wheelers": four,
            "form": form,
            "my_rentals": my_rentals,
        },
    )


@login_required
@require_POST
def rent_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(RentalVehicle, id=vehicle_id, available=True)
    form = RentalInquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.user = request.user
        inquiry.vehicle = vehicle
        inquiry.save()
        messages.success(request, f"Rental request sent for {vehicle.name}.")
        return redirect("transport:private")
    messages.error(request, "Check the rental form and try again.")
    return redirect("transport:private")
