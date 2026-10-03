from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from .utils import haversine_m, normalize_destination


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="transport_profile")
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} profile"


class TravelSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="travel_session")
    destination = models.CharField(max_length=200)
    dest_lat = models.FloatField(null=True, blank=True)
    dest_lng = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    open_to_share = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def same_destination(self, other):
        if normalize_destination(self.destination) and normalize_destination(self.destination) == normalize_destination(
            other.destination
        ):
            return True
        distance = haversine_m(self.dest_lat, self.dest_lng, other.dest_lat, other.dest_lng)
        return distance is not None and distance <= settings.DESTINATION_MATCH_METERS

    def distance_to(self, other):
        return haversine_m(self.lat, self.lng, other.lat, other.lng)


class RideInvite(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DECLINED, "Declined"),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_ride_invites")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_ride_invites")
    destination = models.CharField(max_length=200)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"


class LocalRoute(models.Model):
    BUS = "bus"
    AUTO = "auto"
    MODE_CHOICES = [(BUS, "Local bus"), (AUTO, "Auto rickshaw")]

    mode = models.CharField(max_length=12, choices=MODE_CHOICES)
    name = models.CharField(max_length=160)
    origin = models.CharField(max_length=160)
    destination = models.CharField(max_length=160)
    stops = models.TextField(help_text="One stop per line, in order.")
    timetable = models.CharField(max_length=200, blank=True)
    fare_note = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_routes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("mode", "name")

    def stop_list(self):
        return [line.strip() for line in self.stops.splitlines() if line.strip()]

    def __str__(self):
        return f"{self.get_mode_display()}: {self.name}"


class RentalVehicle(models.Model):
    TWO = "two_wheeler"
    FOUR = "four_wheeler"
    KIND_CHOICES = [(TWO, "Two wheeler"), (FOUR, "Four wheeler")]

    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    name = models.CharField(max_length=160)
    description = models.TextField()
    price_per_day = models.PositiveIntegerField()
    location = models.CharField(max_length=160, default="Imphal")
    image_url = models.URLField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ("kind", "price_per_day")

    def __str__(self):
        return self.name


class RentalInquiry(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rental_inquiries")
    vehicle = models.ForeignKey(RentalVehicle, on_delete=models.CASCADE, related_name="inquiries")
    days = models.PositiveSmallIntegerField(default=1)
    message = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
