from django.urls import path

from . import views

app_name = "transport"

urlpatterns = [
    path("", views.transport_hub, name="hub"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/register/", views.register_view, name="register"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("ride/", views.ride_share, name="ride"),
    path("ride/presence/", views.update_presence, name="presence"),
    path("ride/nearby/", views.nearby_travelers, name="nearby"),
    path("ride/invite/", views.send_ride_invite, name="invite"),
    path("ride/invite/<int:invite_id>/respond/", views.respond_ride_invite, name="respond"),
    path("local/", views.local_routes, name="local"),
    path("local/add/", views.add_local_route, name="add_route"),
    path("private/", views.private_transport, name="private"),
    path("private/rent/<int:vehicle_id>/", views.rent_vehicle, name="rent"),
]
