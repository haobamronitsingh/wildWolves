from django.shortcuts import render
from django.urls import reverse

from .services.youtube import get_trending_cafes, get_trending_places

TRENDING_PLACES = [
    {
        "name": "Loktak Lake",
        "location": "Bishnupur, Manipur",
        "category": "Nature and water",
        "description": "Explore floating phumdis, peaceful waters, and the famous Sendra viewpoint.",
        "image": "wildwolves/images/loktak-lake.jpg",
        "score": 98,
    },
    {
        "name": "Kangla Fort",
        "location": "Imphal West, Manipur",
        "category": "Heritage",
        "description": "Walk through the historic heart of Manipur and discover stories of its royal past.",
        "image": "wildwolves/images/kangla-fort.jpg",
        "score": 94,
    },
    {
        "name": "Shirui Hills",
        "location": "Ukhrul, Manipur",
        "category": "Hills and trekking",
        "description": "Breathe in mountain air and follow trails through the home of the rare Shirui Lily.",
        "image": "wildwolves/images/shirui-lily.jpg",
        "score": 91,
    },
]

CAFES_BY_SPOT = {
    "Loktak Lake": [
        {"name": "Sendra Tourist Hub Cafe", "location": "Sendra, near Loktak Lake", "description": "A relaxed stop for tea, snacks, and a lake view.", "image": "wildwolves/images/loktak-lake.jpg", "score": 88},
        {"name": "Moirang Cafe", "location": "Moirang", "description": "Local flavours and quick bites on the way to Loktak.", "image": "wildwolves/images/loktak-lake.jpg", "score": 82},
        {"name": "Floating View Cafe", "location": "Bishnupur", "description": "A scenic place to slow down after exploring the lake.", "image": "wildwolves/images/loktak-lake.jpg", "score": 79},
    ],
    "Kangla Fort": [
        {"name": "Imphal Heritage Cafe", "location": "Imphal West", "description": "Coffee, local snacks, and a calm break near the fort.", "image": "wildwolves/images/kangla-fort.jpg", "score": 88},
        {"name": "Kangla Corner", "location": "Kangla Road", "description": "A convenient stop for refreshments after sightseeing.", "image": "wildwolves/images/kangla-fort.jpg", "score": 83},
        {"name": "Sana Kitchen", "location": "Imphal", "description": "A popular local-style dining experience for hungry explorers.", "image": "wildwolves/images/kangla-fort.jpg", "score": 80},
    ],
    "Shirui Hills": [
        {"name": "Ukhrul Hill Cafe", "location": "Ukhrul", "description": "Warm drinks and hearty plates before or after a hill walk.", "image": "wildwolves/images/shirui-lily.jpg", "score": 87},
        {"name": "Shirui View Cafe", "location": "Shirui", "description": "A simple local stop with mountain views.", "image": "wildwolves/images/shirui-lily.jpg", "score": 81},
        {"name": "Tangkhul Taste House", "location": "Ukhrul", "description": "Try local flavours and refill before your next trail.", "image": "wildwolves/images/shirui-lily.jpg", "score": 78},
    ],
}


def home(request):
    trending_places = get_trending_places(TRENDING_PLACES)
    query = request.GET.get("q", "").strip()
    search_results = trending_places
    if query:
        search_term = query.casefold()
        search_results = [
            place
            for place in trending_places
            if search_term in " ".join(
                (
                    place["name"],
                    place["location"],
                    place["category"],
                    place["description"],
                )
            ).casefold()
        ]
    logged_in_role = ""
    dashboard_url = ""
    if request.user.is_authenticated:
        if hasattr(request.user, "profile"):
            logged_in_role = "Local guide"
            dashboard_url = reverse("localGuide:guide_dashboard")
        elif hasattr(request.user, "tourist_profile"):
            logged_in_role = "Tourist"
            dashboard_url = reverse("tourist:dashboard")
    return render(request, "home.html", {
        "trending_place": trending_places[0],
        "trending_places": trending_places,
        "search_results": search_results,
        "search_query": query,
        "logged_in_role": logged_in_role,
        "dashboard_url": dashboard_url,
    })


def cafe_recommendations(request):
    places = get_trending_places(TRENDING_PLACES)
    requested_spot = request.GET.get("spot", "").strip()
    spot = next(
        (place for place in places if place["name"].casefold() == requested_spot.casefold()),
        places[0],
    )
    cafes = get_trending_cafes(spot["name"], CAFES_BY_SPOT.get(spot["name"], []))
    return render(request, "cafe_recommendations.html", {
        "spot": spot,
        "cafes": cafes,
        "available_spots": places,
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
