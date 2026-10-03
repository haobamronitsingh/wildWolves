from django.urls import path
from . import views

app_name = 'localGuide'

urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('guide/', views.guide_dashboard, name='guide_dashboard'),
    path('guide/requests/<int:request_id>/accept/', views.accept_assistance_request, name='accept_request'),
    path('guide/requests/<int:request_id>/complete/', views.complete_assistance_request, name='complete_request'),
]