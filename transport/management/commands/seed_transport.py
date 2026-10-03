from django.core.management.base import BaseCommand

from transport.models import LocalRoute, RentalVehicle


ROUTES = [
    {
        "mode": LocalRoute.BUS,
        "name": "ISBT Imphal to Kangla",
        "origin": "ISBT Imphal",
        "destination": "Kangla Fort",
        "stops": "ISBT\nKeishampat\nPaona Bazar\nKangla Gate",
        "timetable": "Every 20–30 min, 6:00–20:00",
        "fare_note": "Approx ₹15–25",
        "notes": "Ask for Kangla / Palace Gate. Last drop is a short walk to the fort.",
    },
    {
        "mode": LocalRoute.BUS,
        "name": "Imphal to Moirang (Loktak)",
        "origin": "Imphal (Moirang stand)",
        "destination": "Moirang / Loktak",
        "stops": "Imphal\nNambol\nBishnupur\nMoirang",
        "timetable": "Hourly morning to evening",
        "fare_note": "Approx ₹50–80",
        "notes": "From Moirang take a shared auto to Sendra or the lake viewpoint.",
    },
    {
        "mode": LocalRoute.AUTO,
        "name": "Paona Bazar to Ima Market",
        "origin": "Paona Bazar",
        "destination": "Ima Keithel",
        "stops": "Paona Bazar\nThangal Bazar\nIma Market",
        "timetable": "Shared autos throughout the day",
        "fare_note": "Shared ₹10–20 · reserved higher",
        "notes": "Confirm shared vs reserved before you sit.",
    },
    {
        "mode": LocalRoute.AUTO,
        "name": "Airport (Tulihal) to Imphal city",
        "origin": "Imphal Airport",
        "destination": "Imphal city / hotel belt",
        "stops": "Airport\nAirport Road\nNorth AOC\nCity hotels",
        "timetable": "On arrival",
        "fare_note": "Negotiate prepaid-style fare; typically ₹250–400 into town",
        "notes": "Use the official pre-paid counter when it is open.",
    },
]

VEHICLES = [
    {
        "kind": RentalVehicle.TWO,
        "name": "Activa 6G",
        "description": "Easy city scooter for markets, Kangla, and short lake day trips.",
        "price_per_day": 500,
        "location": "Thangal Bazar, Imphal",
        "image_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=900&q=80",
        "contact_phone": "0385-2001001",
    },
    {
        "kind": RentalVehicle.TWO,
        "name": "Royal Enfield Classic 350",
        "description": "For hills and longer rides toward Ukhrul when roads are open.",
        "price_per_day": 1200,
        "location": "North AOC, Imphal",
        "image_url": "https://images.unsplash.com/photo-1558981285-6f0c94958bb6?auto=format&fit=crop&w=900&q=80",
        "contact_phone": "0385-2001002",
    },
    {
        "kind": RentalVehicle.FOUR,
        "name": "Maruti Swift Dzire",
        "description": "Sedan with driver-optional self-drive for family trips around Imphal.",
        "price_per_day": 2200,
        "location": "Airport Road, Imphal",
        "image_url": "https://images.unsplash.com/photo-1549924231-f129b911e442?auto=format&fit=crop&w=900&q=80",
        "contact_phone": "0385-2002001",
    },
    {
        "kind": RentalVehicle.FOUR,
        "name": "Mahindra Scorpio",
        "description": "SUV suited to hill roads and group travel to Loktak or Ukhrul.",
        "price_per_day": 3500,
        "location": "Checkon, Imphal",
        "image_url": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?auto=format&fit=crop&w=900&q=80",
        "contact_phone": "0385-2002002",
    },
]


class Command(BaseCommand):
    help = "Insert sample Manipur bus/auto routes and rental vehicles."

    def handle(self, *args, **options):
        for data in ROUTES:
            LocalRoute.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
        for data in VEHICLES:
            RentalVehicle.objects.update_or_create(name=data["name"], defaults=data)
        self.stdout.write(self.style.SUCCESS("Sample routes and rentals are ready."))
