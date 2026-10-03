from django.contrib.auth.models import User
from django.db import models


class TouristProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tourist_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Tourist Profile"


class SOSAlert(models.Model):
    tourist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sos_alerts',
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"SOS from {self.tourist.username} at {self.latitude}, {self.longitude}"


class AssistanceRequest(models.Model):
    PACKAGE_CHOICES = [
        (2, '2 hours - Rs 500'),
        (4, '4 hours - Rs 900'),
        (8, '8 hours - Rs 1,600'),
    ]
    PACKAGE_PRICES = {
        2: 500,
        4: 900,
        8: 1600,
    }
    STATUS_OPEN = 'open'
    STATUS_ACCEPTED = 'accepted'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    tourist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assistance_requests',
    )
    area = models.CharField(max_length=120)
    tourist_count = models.PositiveIntegerField(default=1)
    package_hours = models.PositiveSmallIntegerField(choices=PACKAGE_CHOICES, default=2)
    package_amount = models.PositiveIntegerField(default=500)
    details = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='accepted_assistance_requests',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.tourist.username} - {self.area} ({self.get_status_display()})"

    @property
    def package_label(self):
        return dict(self.PACKAGE_CHOICES).get(self.package_hours, '')
