from django.urls import path

from . import views

app_name = 'tourist'

urlpatterns = [
    path('registerTourist/', views.registerTourist, name='register'),
    path('loginTourist/', views.loginTourist, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
]
