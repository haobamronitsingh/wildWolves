from django.shortcuts import render

from .services.youtube import get_trending_places

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
    trending_places = get_trending_places(TRENDING_PLACES)
    return render(request, "home.html", {
        "trending_place": trending_places[0],
        "trending_places": trending_places,
    })


def login_choices(request):
    return render(request, "auth_choices.html", {
        "title": "Choose how you want to log in",
        "heading": "Welcome back",
        "tourist_url": "tourist:login",
        "guide_url": "localGuide:login",
        "tourist_label": "Tourist",
        "guide_label": "Local guide",
    })


def register_choices(request):
    return render(request, "auth_choices.html", {
        "title": "Choose your account type",
        "heading": "Join WildWolves",
        "tourist_url": "tourist:register",
        "guide_url": "localGuide:register",
        "tourist_label": "Tourist",
        "guide_label": "Local guide",
    })
