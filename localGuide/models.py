from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('mn', 'Manipuri'),
        ('hi', 'Hindi'),
    ]

    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('local', 'Local'),
        ('full_time', 'Full Time'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    service_area = models.CharField(max_length=120, blank=True)
    is_available = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    known_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, default='local')
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
