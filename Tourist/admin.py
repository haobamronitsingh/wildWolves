from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import SOSAlert, TouristProfile


@admin.register(TouristProfile)
class TouristProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('tourist', 'latitude', 'longitude', 'created_at')
    search_fields = ('tourist__username',)
    list_filter = ('created_at',)
