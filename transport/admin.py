from django.contrib import admin

from .models import LocalRoute, RentalInquiry, RentalVehicle, RideInvite, TravelSession, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number")


@admin.register(TravelSession)
class TravelSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "destination", "open_to_share", "updated_at")


@admin.register(RideInvite)
class RideInviteAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "destination", "status", "created_at")


@admin.register(LocalRoute)
class LocalRouteAdmin(admin.ModelAdmin):
    list_display = ("name", "mode", "origin", "destination", "is_active")
    list_filter = ("mode", "is_active")
    search_fields = ("name", "origin", "destination", "stops")


@admin.register(RentalVehicle)
class RentalVehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "price_per_day", "location", "available")
    list_filter = ("kind", "available")


@admin.register(RentalInquiry)
class RentalInquiryAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle", "days", "status", "created_at")
    list_filter = ("status",)
